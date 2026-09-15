import os
from pathlib import Path

os.environ.setdefault("DEV", "CPU")
os.environ.setdefault("XDG_CACHE_HOME", str(Path(__file__).resolve().parents[1] / ".cache"))

from tinygrad.llm.cli import main
if __name__ == "__main__": main()
