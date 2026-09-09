"""Guard the FastAPI Cloud application-directory contract without using secrets."""

import os
import re
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"


def requirement_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


class DeploymentConfigTests(unittest.TestCase):
    def isolated_environment(self) -> dict[str, str]:
        environment = {
            key: value for key, value in os.environ.items()
            if not key.startswith("AWS_")
            and key not in {"DATABASE_URL", "JWT_SECRET_KEY", "PYTHONPATH"}
        }
        environment.update(
            PYTHON_DOTENV_DISABLED="1", PYTHONDONTWRITEBYTECODE="1",
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-deployment-secret-not-a-real-credential",
            AWS_REGION="ap-southeast-2",
            AWS_BEARER_TOKEN_BEDROCK="test-only-not-a-real-bedrock-token",
            AWS_EC2_METADATA_DISABLED="true", KNOWLEDGE_BASE_ID="",
        )
        return environment

    def test_root_requirements_forward_to_one_backend_manifest(self) -> None:
        self.assertEqual(
            requirement_lines(REPO_ROOT / "requirements.txt"),
            ["-r backend/requirements.txt"],
        )

    def test_backend_dependencies_are_self_contained_and_pinned(self) -> None:
        requirements = requirement_lines(BACKEND_ROOT / "requirements.txt")
        self.assertTrue(requirements)
        package_names = []
        for requirement in requirements:
            # No parent paths or nested includes: backend/ must build alone.
            match = re.fullmatch(
                r"([A-Za-z0-9_-]+)(?:\[[A-Za-z0-9_,-]+\])?==[0-9]+(?:\.[0-9]+)+",
                requirement,
            )
            self.assertIsNotNone(match, requirement)
            package_names.append(match.group(1).lower())
        self.assertEqual(len(package_names), len(set(package_names)))
        self.assertTrue(any(line.startswith("fastapi[standard]==") for line in requirements))
        self.assertIn("sqlalchemy", package_names)
        self.assertIn("psycopg2-binary", package_names)
        self.assertIn("boto3", package_names)

    def test_python_version_is_pinned_in_the_application_directory(self) -> None:
        self.assertEqual(
            (BACKEND_ROOT / ".python-version").read_text(encoding="utf-8").strip(),
            "3.13",
        )
        self.assertTrue((BACKEND_ROOT / "main.py").is_file())

    def test_cli_auto_discovers_app_and_starts_without_local_env(self) -> None:
        script = textwrap.dedent("""
            from fastapi_cli.discover import get_import_data
            discovered = get_import_data()
            # backend/__init__.py makes CLI discovery use the package name.
            assert discovered.import_string == "backend.main:app", discovered
            assert discovered.module_config_source == "auto-discovery", discovered
            from database import engine
            assert engine.dialect.name == "sqlite"
            from sqlalchemy import inspect
            assert set(inspect(engine).get_table_names()) == {
                "users", "trips", "knowledge_chunks", "conversations", "messages"
            }
            from fastapi.testclient import TestClient
            from importlib import import_module
            app = getattr(import_module(discovered.module_data.module_import_str), discovered.app_name)
            with TestClient(app) as client:
                assert client.get("/health").json() == {"status": "OK"}
                assert client.get("/docs").status_code == 200
                assert client.get("/api/v1/conversations").status_code == 401
            print("PASS: FastAPI CLI auto-discovery, schema, health, docs, auth boundary")
        """)
        result = subprocess.run(
            [sys.executable, "-B", "-c", script], cwd=BACKEND_ROOT,
            env=self.isolated_environment(), capture_output=True, text=True, timeout=45,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: FastAPI CLI", result.stdout)

    def test_missing_database_configuration_fails_clearly(self) -> None:
        environment = self.isolated_environment()
        environment.pop("DATABASE_URL")
        result = subprocess.run(
            [sys.executable, "-B", "-c", "from fastapi_cli.discover import get_import_data; get_import_data()"],
            cwd=BACKEND_ROOT, env=environment,
            capture_output=True, text=True, timeout=45,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL is not set", result.stderr)

    def test_cli_package_import_without_implicit_working_directory(self) -> None:
        script = textwrap.dedent("""
            import sys
            from pathlib import Path
            from fastapi_cli.discover import get_import_data
            from fastapi.testclient import TestClient
            from importlib import import_module

            original_directory = Path.cwd()
            discovered = get_import_data(path=Path(sys.argv[1]))
            assert discovered.import_string == "backend.main:app", discovered
            assert Path.cwd() == original_directory
            app = getattr(import_module(discovered.module_data.module_import_str), discovered.app_name)
            with TestClient(app) as client:
                assert client.get("/health").json() == {"status": "OK"}
                assert client.get("/api/v1/conversations").status_code == 401
            from database import engine
            assert engine.dialect.name == "sqlite"
        """)
        for working_directory, entrypoint in (
            (BACKEND_ROOT, "main.py"),
            (REPO_ROOT, "backend/main.py"),
        ):
            with self.subTest(working_directory=working_directory):
                # Unlike python -c/-m, a console-script launch does not implicitly
                # place its working directory on sys.path. -P reproduces that.
                result = subprocess.run(
                    [sys.executable, "-P", "-B", "-c", script, entrypoint],
                    cwd=working_directory, env=self.isolated_environment(),
                    capture_output=True, text=True, timeout=45,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_postgresql_pool_checks_stale_connections_and_bounds_connect_time(self) -> None:
        environment = self.isolated_environment()
        environment["DATABASE_URL"] = (
            "postgresql+psycopg2://testuser:testpassword@127.0.0.1:1/testdb"
        )
        script = textwrap.dedent("""
            from unittest.mock import patch
            from sqlalchemy import create_engine
            # Constructing an engine is lazy: this test never opens a connection.
            with patch("sqlalchemy.create_engine", wraps=create_engine) as factory:
                import database
                assert factory.call_args.kwargs["pool_pre_ping"] is True
                assert factory.call_args.kwargs["connect_args"] == {"connect_timeout": 10}
                assert database.engine.dialect.name == "postgresql"
                database.engine.dispose()
        """)
        result = subprocess.run(
            [sys.executable, "-B", "-c", script], cwd=BACKEND_ROOT,
            env=environment, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
