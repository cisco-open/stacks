import pathlib
import json

import hcl2

from ..cmd import config
from ..cmd import context
from ..cmd import preinit
from .. import helpers


def remote_context(ctx, stack=None, environment=None, subenvironment=None, instance=None):  # TODO: explore if this should be a method of context.Context
    assert any([stack, environment, subenvironment, instance])
    remote_path = pathlib.Path(config.STACKS_DIR, stack or ctx.stack, config.LAYERS_DIR, (environment or ctx.env) + (f"@{subenvironment}" if subenvironment else "") + (f"_{instance}" if instance else ""))
    return context.Context(path=ctx.root_dir.joinpath(remote_path), out=ctx.work_dir.joinpath(remote_path, config.OUTPUT_DIR))


def variable(ctx, name, *args, **kwargs):
    remote_ctx = remote_context(ctx=ctx, *args, **kwargs)
    return helpers.hcl2_read(
        [
            pattern
            for pattern in [
                remote_ctx.env_dir.joinpath("env.tfvars"),
                remote_ctx.subenv_dir.joinpath("*.tfvars") if remote_ctx.subenv_dir else None,
                remote_ctx.stacks_dir.joinpath("*.tfvars"),
                remote_ctx.stack_dir.joinpath("*.tfvars"),
                remote_ctx.path.joinpath("*.tfvars"),
            ]
            if pattern
        ]
    )[name]


def terraform_init_headless(ctx, argv, *args, **kwargs):
    remote_ctx = remote_context(ctx=ctx, *args, **kwargs)
    preinit.preinit(ctx=remote_ctx)
    code = helpers.hcl2_read([remote_ctx.work_dir.joinpath("*.tf")])
    helpers.directory_remove(remote_ctx.work_dir)
    helpers.json_write({"terraform": [{"backend": code["terraform"][0]["backend"]}]}, remote_ctx.universe_file)
    helpers.run_command(config.TERRAFORM_PATH, f"-chdir={remote_ctx.work_dir}", "init")  # we cannot avoid pulling providers because we need to know the resources' schema
    return helpers.run_command(config.TERRAFORM_PATH, f"-chdir={remote_ctx.work_dir}", *argv, interactive=False).stdout


def output(ctx, name, *args, **kwargs):
    if ctx.ancestor == ctx.parent and ctx.parent is not None:
        return ""  # empty string so it cannot be iterated upon
    return json.loads(terraform_init_headless(ctx=ctx, argv=["output", "-json", name], *args, **kwargs))


def resource(ctx, address, *args, **kwargs):
    if ctx.ancestor == ctx.parent and ctx.parent is not None:
        return ""  # empty string so it cannot be iterated upon
    return hcl2.loads(terraform_init_headless(ctx=ctx, argv=["state", "show", "-no-color", address], *args, **kwargs))["resource"][0].popitem()[1].popitem()[1]
