type ItinerarySection = {
  title: string;
  lines: string[];
};

function parseItinerary(markdown: string): ItinerarySection[] {
  const sections: ItinerarySection[] = [];
  let current: ItinerarySection | null = null;

  function finishCurrentSection() {
    if (current && current.lines.length > 0) sections.push(current);
  }

  for (const rawLine of markdown.split("\n")) {
    const line = rawLine.trim();

    if (!line) continue;

    if (line.startsWith("## ")) {
      finishCurrentSection();
      current = {
        title: line.replace(/^##\s+/, ""),
        lines: [],
      };
    } else if (/^#{3,6}\s+/.test(line)) {
      const nestedTitle = line.replace(/^#{3,6}\s+/, "");
      const startsNewSection =
        /^(day\s+\d+\b|local food|transportation|practical travel tips|travel tips)/i.test(
          nestedTitle,
        );

      if (startsNewSection) {
        finishCurrentSection();
        current = { title: nestedTitle, lines: [] };
        continue;
      }

      current ??= { title: "Your itinerary", lines: [] };
      current.lines.push("**" + nestedTitle + "**");
    } else if (!line.startsWith("# ")) {
      current ??= { title: "Your itinerary", lines: [] };
      const content = line.replace(/^-\s*/, "");
      if (!/^-{2,}$/.test(content)) current.lines.push(line);
    }
  }

  finishCurrentSection();

  return sections.length
    ? sections
    : [{ title: "Your itinerary", lines: [markdown] }];
}

export function ItineraryContent({ recommendation }: { recommendation: string }) {
  const sections = parseItinerary(recommendation);

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {sections.map((section, sectionIndex) => (
        <article
          key={section.title + "-" + sectionIndex}
          className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm sm:p-7"
        >
          <div className="flex items-start gap-4">
            <span className="grid size-9 shrink-0 place-items-center rounded-full bg-amber-100 text-sm font-bold text-amber-900">
              {String(sectionIndex + 1).padStart(2, "0")}
            </span>
            <div>
              <h2 className="text-lg font-semibold leading-7 text-slate-950">
                {section.title}
              </h2>
              <div className="mt-3 space-y-2.5 text-sm leading-6 text-slate-600">
                {section.lines.map((line, lineIndex) => {
                  const isBullet = line.startsWith("-");
                  const isEmphasis = line.includes("**");

                  return (
                    <p
                      key={line + "-" + lineIndex}
                      className={[
                        isBullet
                          ? "relative pl-4 before:absolute before:left-0 before:text-teal-700 before:content-['•']"
                          : "",
                        isEmphasis ? "font-semibold text-slate-800" : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                    >
                      {line.replace(/^-\s*/, "").replace(/\*\*/g, "")}
                    </p>
                  );
                })}
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
