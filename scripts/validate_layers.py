#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from warm_company.cli import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "validate-layers", *sys.argv[1:]]
    raise SystemExit(main())
