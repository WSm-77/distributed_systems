from __future__ import annotations

import importlib
import logging


def main() -> None:
    serve = importlib.import_module("src.app.server").serve
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    serve()


if __name__ == "__main__":
    main()
