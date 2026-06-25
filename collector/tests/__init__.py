"""Test package. Bootstrap sys.path so tests can `import contract` (collector dir) and
`from _util import ...` (this dir), whether run via `unittest discover` or directly."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_COLLECTOR = _HERE.parent
for _p in (str(_COLLECTOR), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
