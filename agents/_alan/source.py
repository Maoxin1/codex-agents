"""Private source access; shared engine is installed with this agent."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _book_sources.epub import main

if __name__ == "__main__":
    raise SystemExit(main(Path(__file__).resolve().parent))
