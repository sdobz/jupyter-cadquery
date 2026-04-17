import ast
import json
from pathlib import Path
import sys

import nbformat


def validate_ipynb(path):
    with open(path, "r", encoding="utf-8") as fd:
        nb = json.load(fd)
    nbformat.validate(nb)


def validate_marimo_py(path):
    content = Path(path).read_text(encoding="utf-8")
    ast.parse(content)
    if "import marimo" not in content:
        raise ValueError("Missing 'import marimo'")
    if "marimo.App(" not in content:
        raise ValueError("Missing 'marimo.App(...)'")


def main(argv):
    if len(argv) < 2:
        print("Usage: python validate_nb.py <notebook-path> [<notebook-path> ...]")
        return 1

    exit_code = 0
    for file_arg in argv[1:]:
        path = Path(file_arg)
        try:
            if path.suffix == ".ipynb":
                validate_ipynb(path)
            elif path.suffix == ".py":
                validate_marimo_py(path)
            else:
                raise ValueError(f"Unsupported notebook type: {path.suffix}")
            print(f"{path}: ==> OK")
        except Exception as ex:  # pylint: disable=broad-except
            print(f"{path}: ==> ERROR ({ex})")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
