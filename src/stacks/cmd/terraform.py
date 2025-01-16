from . import config
from . import render
from .. import helpers


def terraform(ctx, init="auto", args=[]):
    render.render(ctx=ctx, init=init)
    return helpers.run_command(config.TERRAFORM_PATH, f"-chdir={ctx.work_dir}", *args)
