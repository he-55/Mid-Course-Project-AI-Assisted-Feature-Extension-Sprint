import os
import sys

# Ensure root directory is on sys.path when running pytest from subdirectories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
