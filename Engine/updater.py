import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set


class ImportUpdater(ast.NodeTransformer):
    """Walks the AST and updates import statements based on a mapping."""

    def __init__(self, mapping):
        self.mapping = mapping

    def _get_updated_name(self, name):
        for old_import, new_import in self.mapping.items():
            if name == old_import:
                return new_import
            elif name.startswith(old_import + "."):
                return name.replace(old_import + ".", new_import + ".", 1)
        return name

    def visit_Import(self, node):
        new_names = []
        for alias in node.names:
            updated_name = self._get_updated_name(alias.name)
            new_names.append(ast.alias(name=updated_name, asname=alias.asname))
        node.names = new_names
        return node

    def visit_ImportFrom(self, node):
        if node.module:
            node.module = self._get_updated_name(node.module)
        return node


def update_python_imports(file_path, import_mapping):
    """Reads a Python file, updates imports using the AST, and overwrites the file."""
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    transformer = ImportUpdater(import_mapping)
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    updated_code = ast.unparse(modified_tree)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_code)

    print(f"Successfully updated imports in {file_path}")


def collect_dependency_packages(project_root: Path) -> Set[str]:
    """Collect importable package names from Python files under the project."""
    packages: Set[str] = set()
    for path in project_root.rglob('*.py'):
        if 'venv' in path.parts or '.git' in path.parts or '__pycache__' in path.parts:
            continue
        try:
            source = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] not in {'os', 'sys', 'json', 'pathlib', 'typing', 'ast', 'dataclasses', 'subprocess', 'importlib', 'math', 'random', 'time', 'uuid', 'logging', 'collections', 'itertools', 'functools', 'enum', 'statistics', 're', 'shutil', 'argparse', 'copy', 'weakref', 'threading'}:
                        packages.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split('.')[0]
                if module not in {'os', 'sys', 'json', 'pathlib', 'typing', 'ast', 'dataclasses', 'subprocess', 'importlib', 'math', 'random', 'time', 'uuid', 'logging', 'collections', 'itertools', 'functools', 'enum', 'statistics', 're', 'shutil', 'argparse', 'copy', 'weakref', 'threading'}:
                    packages.add(module)
    return packages


def check_and_install_dependencies(project_root: Path, install_missing: bool = True) -> Dict[str, object]:
    """Check whether required third-party packages are installed and install them if needed."""
    required_packages = sorted(collect_dependency_packages(project_root))
    results: Dict[str, object] = {'checked': required_packages, 'missing': [], 'installed': []}

    for package in required_packages:
        try:
            importlib.import_module(package)
        except Exception:
            results['missing'].append(package)
            if install_missing:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    results['installed'].append(package)
                except subprocess.CalledProcessError:
                    pass
    return results


def ensure_runtime_dependencies(project_root: Path | None = None, install_missing: bool = True) -> Dict[str, object]:
    """Run dependency checks before the game launches."""
    root = Path(project_root or Path(__file__).resolve().parent.parent)
    return check_and_install_dependencies(root, install_missing=install_missing)


if __name__ == "__main__":
    ensure_runtime_dependencies()