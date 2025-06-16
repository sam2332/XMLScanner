import os

def shorten_path(filepath, segments=7):
    parts = filepath.replace("\\", "/").split("/")
    return "/".join(parts[-segments:]) if len(parts) > segments else filepath
def get_cpu_count():
    """Get the number of logical CPUs available"""
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1  # Fallback to 1 if os.cpu_count() fails