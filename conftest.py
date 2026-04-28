import os
import sys

# Add project root to sys.path so imports work
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure working directory is project root (some modules depend on this)
os.chdir(project_root)
