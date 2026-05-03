import sys
from pathlib import Path

# Ensure `from app.xxx import ...` works when pytest is run from project root
sys.path.insert(0, str(Path(__file__).parent))
