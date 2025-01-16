import fnmatch
import shutil


def copy_files(src, dst, include=None, prefix=""):
    assert src.is_dir()

    for item in src.iterdir():
        if item.is_file() and any(fnmatch.fnmatch(item.name, pattern) for pattern in include):
            dst.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(
                src=item,
                dst=dst.joinpath(f"{prefix}{item.name}"),
            )


def directory_remove(path, keep=[]):
    """Remove 'path' dir, but preserve any paths in 'keep'.
    You can 'keep' paths in 'path', but not in any of its subdirectories.

    Keyword arguments:
      path[pathlib.Path]: path to directory
      keep[list]: paths to keep
    """
    if path.is_dir():
        for item in path.iterdir():
            if item.name not in keep:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
