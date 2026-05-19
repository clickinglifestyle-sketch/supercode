import sys
import os

# Ensure the project root is importable regardless of cwd
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from main import cli


def main():
    cli()


if __name__ == "__main__":
    main()
