#!/usr/bin/env python3

import glob
import os
import pathlib

import helpers


# define context
cwd         = pathlib.Path().cwd()                              # current working directory
rootdir     = cwd.parent.parent.parent.parent                   # repository root
envsdir     = rootdir.joinpath("environments")                  # where environment definitions live
stacksdir   = rootdir.joinpath("stacks")                        # where stack definitions live
stackdir    = cwd.parent.parent                                 # where this stack's definition lives
basedir     = stackdir.joinpath("base")                         # where this stack's base code lives
workdir     = cwd.joinpath("stacks.out")                        # where init/plan/apply will happen
stack       = stackdir.name                                     # the stack's name
layer       = cwd.name                                          # the layer's name
layer_split = layer.split("_", 1)                               # split environment and instance
env         = layer_split[0]                                    # the layer's environment's name
envdir      = envsdir.joinpath(env)                             # the layer's environment directory
instance    = layer_split[1] if len(layer_split) > 1 else None  # the layer's instance's name, otherwise None
# validate context
assert(basedir.exists())
assert(envdir.exists())

# remove workdir to avoid interference between runs
helpers.directory_remove(workdir, keep=[
    ".terraform",           # keep .terraform to avoid re-init
    ".terraform.lock.hcl",  # keep .terraform.lock.hcl to avoid re-init
])

# read variables
variables = {
    **helpers.hcl2_read([
        envdir.joinpath("environment.tfvars"),
        stacksdir.joinpath("common.tfvars"),
        stackdir.joinpath("stack.tfvars"),
        cwd.joinpath("layer.tfvars"),
    ]),
    "stacks-root": "../../../../..",                 # repository root, relative to workdir
    "stacks-path": f"stacks/{stack}/layer/{layer}",  # layer path, relative to repository root
    "stacks-stack": stack,                           # stack name
    "stacks-layer": layer,                           # stack layer
    "stacks-environment": env,                       # layer environment
    "stacks-instance": instance or "",               # layer instance (if exists)
}

# merge stack and layer files
reserved = [".terraform", ".terraform.lock.hcl", "stacks.tf.json", "zzz.auto.tfvars.json"]
helpers.directory_copy(basedir, workdir, ignore=reserved)
helpers.directory_copy(cwd, workdir, ignore=reserved+[
    "layer.tfvars",
    pathlib.Path(os.getenv("PLANFILE","default.tfplan")).name,  # do not copy plan files (binary)
    pathlib.Path(os.getenv("SHOWFILE","default.json")).name,    # do not copy plan files (json)
])

files_tf     = sorted(glob.glob(str(workdir.joinpath("*.tf"))))
files_tfvars = sorted(glob.glob(str(workdir.joinpath("*.auto.tfvars"))))

# render files
helpers.jinja2_render(files_tf, {"var": variables})

# initialize universe
universe = {"terraform": {}, "provider": [], "variable": {}}

# configure remote state backend
universe["terraform"]["backend"] = {"s3": {
    **helpers.hcl2_read([envdir.joinpath("backend.tfvars")]),
    "key": f"layers/{stack}/{f'{instance}/' if instance else ''}terraform.tfstate",
}}

# add missing variables' declarations
variables_declared = [
    list(variable.keys())[0]
    for variable in helpers.hcl2_read(files_tf).get("variable", [])
]
for variable in {**variables, **helpers.hcl2_read(files_tfvars)}.keys():  # also autodeclare variables in *.auto.tfvars files
    if variable not in variables_declared:
        universe["variable"][variable] = {}

# configure AWS providers
regions = []  # CHANGEME (the list of regions you operate in)
def provider_aws_append(region, role, alias=None):
    global universe, variables, stack, env
    universe["provider"].append({"aws": {
        **variables.get("stacks-provider-aws-extra-args", {}),
        **({"alias": alias} if alias else {}),
        "region": region,
        "assume_role": [{"role_arn": role}],
        "default_tags": [{"tags": {
            **variables.get("stacks-provider-aws-extra-tags", {}),
            "stacks-path": variables["stacks-path"],
        }}],
    }})
# inject default provider
provider_aws_append(variables["region"], variables["role_arn"])
# inject default provider in other regions
for region in regions:
    provider_aws_append(region, variables["role_arn"], region)
# inject all other environments' default providers
for path in envsdir.iterdir():
    if not path.is_dir():
        continue
    try:
        environment = helpers.hcl2_read([path.joinpath("environment.tfvars")])
        provider_aws_append(environment["region"], environment["role_arn"], path.name)
        # inject all other environments' other regions' providers
        for region in regions:
            provider_aws_append(region, environment["role_arn"], f"{path.name}_{region}")
    except KeyError:
        continue

# persist universe and variables
helpers.json_write(universe, workdir.joinpath("stacks.tf.json"))
helpers.json_write(variables, workdir.joinpath("zzz.auto.tfvars.json"))  # 'zzz' so that it has the topmost precedence
