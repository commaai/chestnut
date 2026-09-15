import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DEV", "USB+AMD:LLVM")
os.environ.setdefault("HCQ2", "0")
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
sys.path.insert(0, str(ROOT / "tinygrad_repo"))
