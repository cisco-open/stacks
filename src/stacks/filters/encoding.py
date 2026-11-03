import json

import yaml


def jsondecode(ctx, data, *args, **kwargs):
    return json.loads(data)


def jsonencode(ctx, data, *args, **kwargs):
    return json.dumps(data)


def yamldecode(ctx, data, *args, **kwargs):
    return yaml.safe_load(data)


def yamlencode(ctx, data, *args, **kwargs):
    return yaml.safe_dump(data)
