import json


def jsondecode(ctx, data, *args, **kwargs):
    return json.loads(data)


def jsonencode(ctx, data, *args, **kwargs):
    return json.dumps(data)
