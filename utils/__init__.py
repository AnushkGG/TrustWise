"""
TrustWise utils package.
This file ensures the project root is always on sys.path,
so imports like 'from utils.config import Config' work
regardless of what directory Python is launched from.
"""
import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
