#!/usr/bin/env python3

# Copyright 2024 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fnmatch
import glob
import json
import os
import pathlib
import shutil
import tempfile

import deepmerge
import hcl2
import jinja2
import yaml

import filters
from tools import encryption_decrypt


def directory_copy(srcpath, dstpath, ignore=[]):
    """Copy the contents of the dir in 'srcpath' to the dir in 'dstpath'.

    Keyword arguments:
      srcpath[str]: path to source directory
      dstpath[str]: path to destination directory
      ignore[list]: files in srcpath to not ignore when copying
    """
    srcpath = pathlib.Path(srcpath)
    dstpath = pathlib.Path(dstpath)
    def ignorefunc(parent, items):
        return [
            item
            for item in items
            if (
                item in ignore
                or item == dstpath.name
                or parent == dstpath.name
                or any(fnmatch.fnmatch(item, pattern) for pattern in ignore)
            )
        ]
    shutil.copytree(srcpath, dstpath, ignore=ignorefunc, dirs_exist_ok=True)


def directory_remove(path, keep=[]):
    """Remove directory in 'path', but preserve any files in 'keep'.

    Keyword arguments:
      path[str]: path to directory
      keep[list]: files in directory to keep
    """
    path = pathlib.Path(path)
    if not path.is_dir():
        return

    for item in path.iterdir():
        if item.name not in keep:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()


def json_read(patterns):
    """Read JSON files in 'patterns' and return their merged contents.

    Keyword arguments:
      patterns[str/list]: pattern/s to JSON file/s, in ascending order of priority
    """
    assert(isinstance(patterns, list))
    data = {}
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if not path.is_file():
                continue
            with open(path, "r") as f:
                data = deepmerge.always_merger.merge(data, json.load(f))
    return data


def json_write(data, path, indent=2):
    """Write 'data' to file in 'path' in JSON format.

    Keyword arguments:
      path[str]: destination file path
      data[any]: JSON-serializable data structure to write to file
      indent[int,optional]: number of spaces to indent JSON levels with
    """
    with open(pathlib.Path(path), "w") as f:
        json.dump(data, f, indent=indent)


def yaml_read(patterns):
    """Read YAML files in 'patterns' and return their merged contents.

    Keyword arguments:
      patterns[str/list]: pattern/s to YAML file/s, in ascending order of priority
    """
    assert(isinstance(patterns, list))
    data = {}
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if not path.is_file():
                continue
            with open(path, "r") as f:
                data = deepmerge.always_merger.merge(data, yaml.safe_load(f))
    return data


def yaml_write(data, path, indent=2, width=1000):
    """Write 'data' to file in 'path' in YAML format.

    Keyword arguments:
      path[str]: destination file path
      data[any]: YAML-serializable data structure to write to file
    """
    with open(pathlib.Path(path), "w") as f:
        yaml.dump(data, f, indent=indent, width=width)


def hcl2_read(patterns):
    """Read HCL2 files in 'patterns' and return their merged contents.

    Keyword arguments:
      patterns[str/list]: pattern/s to HCL2 file/s, in ascending order of priority
    """
    assert(isinstance(patterns, list))
    data = {}
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if not path.is_file():
                continue
            with open(path, "r") as f:
                data = deepmerge.always_merger.merge(data, hcl2.load(f))
    return hcl2_decrypt(data)


def hcl2_decrypt(data):
    """Decrypts all strings in 'data'.

    Keyword arguments:
      data[any]: any HCL2-sourced data structure
    """
    if isinstance(data, str) and data.startswith("ENC[") and data.endswith("]"):
        key_path = os.getenv("STACKS_PRIVATE_KEY_PATH")
        if not key_path:
            raise Exception("could not decrypt data: STACKS_PRIVATE_KEY_PATH is not set")
        if not pathlib.Path(key_path).exists():
            raise Exception(f"could not decrypt data: STACKS_PRIVATE_KEY_PATH ({key_path}) does not exist")
        return encryption_decrypt.main(data, key_path)

    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = hcl2_decrypt(data[i])

    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = hcl2_decrypt(v)

    return data


def jinja2_render(patterns, data):
    """Overwrite files in 'patterns' with their Jinja2 render.

    Keyword arguments:
      patterns[str/list]: pattern/s of text file/s
      data[dict]: variables to render files with
    """
    assert(isinstance(patterns, list))
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if not path.is_file():
                continue
            try:
                with open(path, "r") as fin:
                    template = jinja2.Template(fin.read())

                rendered = template.render(data | {
                    func.__name__: func
                    for func in filters.__all__
                })

                with open(path, "w") as fout:
                    fout.write(rendered)
            except jinja2.exceptions.UndefinedError as e:
                print(f"Failure to render {path}: {e}", file=sys.stderr)
                sys.exit(1)
            except jinja2.exceptions.TemplateSyntaxError as e:
                print(f"Failure to render {path} at line {e.lineno}, in statement {e.source}: {e}", file=sys.stderr)
                sys.exit(1)
