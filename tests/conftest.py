# tests/conftest.py
import sys
from pathlib import Path

# Determine the absolute path to the 'src' directory relative to this file.
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
