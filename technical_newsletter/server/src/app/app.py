from __future__ import annotations

import importlib
import logging
from src.app.server import serve

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    serve()


if __name__ == "__main__":
    main()
