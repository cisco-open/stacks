def deepformat(ctx, value, params):
    if isinstance(value, str):
        return value.format(**params)
    elif isinstance(value, list):
        return [deepformat(item, params) for item in value]
    elif isinstance(value, dict):
        return {deepformat(key, params): deepformat(value, params) for key, value in value.items()}
    return value
