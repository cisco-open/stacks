import glob
import json
import pathlib

import hcl2
import yaml

from .crypto import decrypt
from .merge import merge


def config_read(patterns, should_decrypt, must_decrypt, decoderfunc, **decoderargs):
    """Read configuration files in 'patterns' using 'decoderfunc' and return their merged contents.

    Keyword arguments:
      patterns[list]: patterns to configuration files, in ascending order of priority
      should_decrypt[bool]: whether it should try to decrypt data or not
      must_decrypt[bool]: whether decryption should succeed (if False and fails, returns encrypted value)
      decoderfunc[function]: function that parses a given configuration file into a data structure
      decoderargs[dict]: keyword arguments to pass to decoderfunc
    """
    assert isinstance(patterns, list)
    data = {}
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if path.is_file():
                with open(path, "r") as f:
                    data = merge(data, decoderfunc(f, **decoderargs))
    return decrypt(data, must_decrypt=must_decrypt) if should_decrypt else data


def json_read(patterns, should_decrypt=True, must_decrypt=True):
    return config_read(patterns, should_decrypt, must_decrypt, json.load)


def yaml_read(patterns, should_decrypt=True, must_decrypt=True):
    return config_read(patterns, should_decrypt, must_decrypt, yaml.safe_load)


def hcl2_read(patterns, should_decrypt=True, must_decrypt=True):
    return config_read(patterns, should_decrypt, must_decrypt, hcl2.load)


def config_write(data, path, encoderfunc, **encoderargs):
    """Write 'data' to file in 'path' using 'encoderfunc' for formatting.

    Keyword arguments:
      data[any]: structure to write to file
      path[pathlib.Path]: destination file path
      encoderfunc[function]: function that formats a given data structure into a configuration file
      encoderargs[dict]: keyword arguments to pass to encoderfunc
    """
    with open(path, "w") as f:
        encoderfunc(data, f, **encoderargs)


def json_write(data, path):
    config_write(data, path, json.dump, indent=2)


def yaml_write(data, path):
    config_write(data, path, yaml.dump, indent=2, width=1000)
