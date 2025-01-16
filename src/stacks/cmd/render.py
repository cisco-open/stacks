from . import config
from . import preinit
from .. import helpers


def render(ctx, init="auto"):
    preinit.preinit(ctx=ctx)

    if init == "always" or (init == "auto" and not ctx.terraform_dir.joinpath("terraform.tfstate").exists()):
        helpers.run_command(config.TERRAFORM_PATH, f"-chdir={ctx.work_dir}", "init")
