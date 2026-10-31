<<<<<<< HEAD
=======
#!/usr/bin/env python3
>>>>>>> 2cdb6f8 (Last changes)
"""Runner script with proper path setup"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from main import main

if __name__ == "__main__":
    main()