import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set

print("Checking for required dependencies...")
print("If you are running this script in a virtual environment, make sure it is activated.")

try:
    import pygame
except Exception:  # pragma: no cover - fallback if pygame is unavailable
    pygame = None


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
    """Collect third-party packages that the shared imports module requires."""
    imports_file = project_root / 'Engine' / 'config' / 'imports.py'
    if not imports_file.exists():
        return set()

    packages: Set[str] = set()
    try:
        source = imports_file.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return set()

    tree = ast.parse(source, filename=str(imports_file))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if module_name not in {'os', 'sys', 'json', 'pathlib', 'typing', 'ast', 'dataclasses', 'subprocess', 'importlib', 'math', 'random', 'time', 'uuid', 'logging', 'collections', 'itertools', 'functools', 'enum', 'statistics', 're', 'shutil', 'argparse', 'copy', 'weakref', 'threading'}:
                    packages.add(module_name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module.split('.')[0]
            if module_name not in {'os', 'sys', 'json', 'pathlib', 'typing', 'ast', 'dataclasses', 'subprocess', 'importlib', 'math', 'random', 'time', 'uuid', 'logging', 'collections', 'itertools', 'functools', 'enum', 'statistics', 're', 'shutil', 'argparse', 'copy', 'weakref', 'threading'}:
                packages.add(module_name)
    return packages


def _show_permission_prompt(packages: List[str]) -> bool:
    """Show a simple confirmation window before installing dependencies."""
    if pygame is None:
        return True

    try:
        pygame.init()
        pygame.display.init()
        screen = pygame.display.set_mode((420, 180))
        pygame.display.set_caption('Install dependencies?')
        screen.fill((18, 18, 24))

        font = pygame.font.SysFont('arial', 18)
        message = 'The game needs to install/update dependencies:'
        detail = ', '.join(packages)
        lines = [message, detail, '', 'Allow this?']
        y = 24
        for line in lines:
            text = font.render(line, True, (240, 240, 240))
            screen.blit(text, (24, y))
            y += 24

        pygame.draw.rect(screen, (70, 120, 220), pygame.Rect(90, 120, 90, 34), border_radius=8)
        pygame.draw.rect(screen, (180, 80, 80), pygame.Rect(240, 120, 90, 34), border_radius=8)
        confirm_text = font.render('Yes', True, (255, 255, 255))
        cancel_text = font.render('No', True, (255, 255, 255))
        screen.blit(confirm_text, (124, 128))
        screen.blit(cancel_text, (278, 128))
        pygame.display.flip()

        waiting = True
        choice = False
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if 90 <= event.pos[0] <= 180 and 120 <= event.pos[1] <= 154:
                        choice = True
                        waiting = False
                    elif 240 <= event.pos[0] <= 330 and 120 <= event.pos[1] <= 154:
                        waiting = False
            pygame.time.delay(20)

        pygame.quit()
        return choice
    except Exception:
        return True


def check_and_install_dependencies(project_root: Path, install_missing: bool = True) -> Dict[str, object]:
    """Check whether required third-party packages are installed and install them if needed."""
    required_packages = sorted(collect_dependency_packages(project_root))
    results: Dict[str, object] = {'checked': required_packages, 'missing': [], 'installed': []}

    for package in required_packages:
        try:
            importlib.import_module(package)
        except Exception:
            results['missing'].append(package)

    if install_missing and results['missing']:
        allow_install = _show_permission_prompt(results['missing'])
        if allow_install:
            for package in results['missing']:
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