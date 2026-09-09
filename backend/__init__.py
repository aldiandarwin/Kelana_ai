"""Keep the course's flat imports compatible with package-based CLI startup.

FastAPI CLI discovers ``backend.main:app`` and adds the repository root to its
module search path. Console-script launches do not also add the working
directory, so imports such as ``from database import ...`` need this explicit
backend path. Local ``uvicorn main:app`` and migration/ingestion commands keep
their existing behavior; the process working directory is never changed.
"""

import sys
from pathlib import Path

_backend_directory = str(Path(__file__).resolve().parent)
if _backend_directory not in sys.path:
    sys.path.insert(0, _backend_directory)
