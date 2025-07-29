def file(ctx, path, *args, **kwargs):
    with open(path) as f:
        return f.read()
