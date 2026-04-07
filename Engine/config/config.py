import os

# Configuration constants
CONFIGURATION = "CONFIGURATION"
CONTENTS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Contents')
RESOURCES_PATH = os.path.join(CONTENTS_PATH, 'Resources')
RESOURCE_MANIFEST_FILE = os.path.join(RESOURCES_PATH, 'resource_paths.txt')

def get_all_resources(base_path):
    """
    Recursively scans the base_path and returns a dictionary of relative paths to absolute paths.
    Keys are relative paths with forward slashes, values are absolute file paths.
    """
    resources = {}
    for root, dirs, files in os.walk(base_path):
        rel_root = os.path.relpath(root, base_path)
        if rel_root == '.':
            rel_root = ''
        for file in files:
            key = os.path.join(rel_root, file).replace(os.sep, '/')
            resources[key] = os.path.join(root, file)
    return resources

# Dictionary containing all resources with relative paths as keys
ALL_RESOURCES = get_all_resources(RESOURCES_PATH)