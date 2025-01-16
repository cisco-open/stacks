import deepmerge


def merge(a, b):
    """Merges the contents of 'a' and 'b'.

    Keyword arguments:
      a[any]: any data structure
      b[any]: any data structure
    """
    if isinstance(a, dict) and isinstance(b, dict):
        for key in list(b.keys()):
            if key in a and key.endswith("_override"):  # TODO: remove this and use bare deepmerge
                # Ideally, this should be handled by the config language instead (i.e. HCL).
                # This only works with top-level keys because deepmerge won't letme define a custom strategy recursively.
                a[key] = b[key]
                b.pop(key)
    return deepmerge.always_merger.merge(a, b)
