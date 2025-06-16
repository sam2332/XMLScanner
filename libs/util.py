def shorten_path(filepath, segments=7):
    parts = filepath.replace("\\", "/").split("/")
    return "/".join(parts[-segments:]) if len(parts) > segments else filepath
