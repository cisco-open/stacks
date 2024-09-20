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

import glob
import pathlib

import git

import helpers


# define context
cwd         = pathlib.Path().cwd()                              # current working directory
rootdir     = cwd.parent.parent.parent.parent.parent            # repository root
envsdir     = rootdir.joinpath("environments")                  # where environment definitions live
stacksdir   = rootdir.joinpath("stacks")                        # where stack definitions live
stackdir    = cwd.parent.parent.parent                          # where this stack's definition lives
workdir     = cwd                                               # where plan/apply will happen
tfdir       = workdir.joinpath(".terraform")                    # the .terraform directory
modulesdir  = tfdir.joinpath("modules")                         # where child modules live
stack       = stackdir.name                                     # the stack's name
layer       = cwd.parent.name                                   # the layer's name
layer_split = layer.split("_", 1)                               # split environment and instance
env         = layer_split[0]                                    # the layer's environment's name
envdir      = envsdir.joinpath(env)                             # the layer's environment directory
instance    = layer_split[1] if len(layer_split) > 1 else None  # the layer's instance's name, otherwise None

# read variables
variables = {
    **helpers.hcl2_read([
        envdir.joinpath("environment.tfvars"),
        stacksdir.joinpath("*.common.tfvars"), stacksdir.joinpath("common.tfvars"),
        stackdir.joinpath("*.stack.tfvars"), stackdir.joinpath("stack.tfvars"),
        cwd.joinpath("*.layer.tfvars"), cwd.joinpath("layer.tfvars"),
    ]),
    "stacks-root": "../../../../..",                 # repository root, relative to workdir
    "stacks-path": f"stacks/{stack}/layer/{layer}",  # layer path, relative to repository root
    "stacks-stack": stack,                           # stack name
    "stacks-layer": layer,                           # stack layer
    "stacks-environment": env,                       # layer environment
    "stacks-instance": instance or "",               # layer instance (if exists)
}

for module in helpers.json_read([modulesdir.joinpath("modules.json")]).get("Modules", []):
    # ignore root module
    if module["Key"] == "":
        continue

    moduledir = workdir.joinpath(module["Dir"])

    # remove changes to avoid interference between runs
    try:
        repo = git.Repo(moduledir)
        repo.git.reset("--hard")
        repo.git.clean("--force")
    except git.exc.InvalidGitRepositoryError:  # use git if the module doesn't to keep track of initial state between runs
        repo = git.Repo.init(moduledir)
        repo.config_writer().set_value("user", "name", "Stacks").release()
        repo.config_writer().set_value("user", "email", "stacks@example.com").release()
        repo.git.add(".")
        repo.git.commit("-m", "stacks: postinit checkpoint")

    # render files
    helpers.jinja2_render([workdir.joinpath("*.tf")], {"var": variables})
