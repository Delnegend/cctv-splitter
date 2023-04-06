
def norm(input_path: str, absolute = False):
    from os import path, getcwd
    """Normalize path"""
    if absolute:
        input_path = path.abspath(input_path) if not path.isabs(input_path) else input_path
    else:
        input_path = path.relpath(input_path, getcwd())
    return path.normpath(input_path).replace("\\", "/")