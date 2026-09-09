import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { Script } from "node:vm";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ts from "typescript";

const require = createRequire(import.meta.url);

// Execute the real leaf components without starting Next.js or a backend.
// Only framework Link and shared auth-dependent navigation are replaced.
function loadSource(relativePath) {
  const filename = fileURLToPath(new URL(`../${relativePath}`, import.meta.url));
  const output = ts.transpileModule(readFileSync(filename, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
    fileName: filename,
  }).outputText;
  const exports = {};
  const localRequire = (name) => {
    if (name.endsWith(".css")) return {};
    if (name === "next/link") {
      return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    }
    if (name === "@/components/SiteHeader") {
      return { SiteHeader: () => React.createElement("header") };
    }
    if (name === "@/components/SiteFooter") {
      return { SiteFooter: () => React.createElement("footer") };
    }
    return require(name);
  };
  new Script(`(function(exports, require) {${output}\n})`, { filename })
    .runInThisContext()(exports, localRequire);
  return exports;
}

function findElement(element, type) {
  if (!React.isValidElement(element)) return undefined;
  if (element.type === type) return element;
  for (const child of React.Children.toArray(element.props.children)) {
    const found = findElement(child, type);
    if (found) return found;
  }
}

test("public pages remain public while account routes require authentication", () => {
  const { requiresAuthentication } = loadSource("lib/authRoutes.ts");
  for (const path of ["/about", "/login", "/register", "/missing-page", "/trips-other"]) {
    assert.equal(requiresAuthentication(path), false, path);
  }
  for (const path of ["/", "/trips", "/trips/42", "/assistant", "/chat", "/profile"]) {
    assert.equal(requiresAuthentication(path), true, path);
  }
});

test("404 gives public recovery links", () => {
  const Component = loadSource("app/not-found.tsx").default;
  const html = renderToStaticMarkup(React.createElement(Component));
  assert.match(html, /404/);
  assert.match(html, /href="\/"/);
  assert.match(html, /href="\/about"/);
});

test("About explains actual features, author and AI privacy limitations", () => {
  const Component = loadSource("app/about/page.tsx").default;
  const html = renderToStaticMarkup(React.createElement(Component));
  for (const text of ["Aldian Darwin Putra", "Knowledge Assistant", "Chat reconstructs", "Amazon Bedrock", "Avoid sharing passport numbers"]) {
    assert.ok(html.includes(text), text);
  }
});

for (const path of ["app/error.tsx", "app/global-error.tsx", "app/trips/error.tsx"]) {
  test(`${path} hides internal details and wires the Next.js retry callback`, () => {
    const Component = loadSource(path).default;
    let retryCount = 0;
    const element = Component({
      error: new Error("internal-database-credential-do-not-display"),
      retry: () => { retryCount += 1; },
    });
    const html = renderToStaticMarkup(element);
    assert.ok(!html.includes("internal-database-credential"));
    assert.match(html, /role="alert"/);
    findElement(element, "button").props.onClick();
    assert.equal(retryCount, 1);
    if (path.includes("global-error")) assert.match(html, /<html lang="en">/);
  });
}

test("loading screen announces status and supports reduced motion", () => {
  const Component = loadSource("app/loading.tsx").default;
  const html = renderToStaticMarkup(React.createElement(Component));
  assert.match(html, /role="status"/);
  assert.match(html, /aria-busy="true"/);
  assert.match(html, /motion-reduce:animate-none/);
});
