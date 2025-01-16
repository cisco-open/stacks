import hcl2

from . import terraform
from . import context
from . import config
from . import render
from .. import helpers


def _list(ctx):
    terraform.terraform(ctx=ctx, args=["state", "list"])


def _import(address, _id, ctx):
    terraform.terraform(ctx=ctx, args=["import", address, _id])


def remove(address, ctx):
    terraform.terraform(ctx=ctx, args=["state", "rm", address])


def move(from_address, to_path, to_address, ctx):
    render.render(ctx=ctx)
    _id = list(list(hcl2.loads(helpers.run_command(config.TERRAFORM_PATH, f"-chdir={ctx.work_dir}", "state", "show", "-no-color", from_address, interactive=False).stdout)["resource"][0].items())[0][1].items())[0][1]["id"]  # this is ugly but it works, do NOT touch
    _import(ctx=context.Context(path=to_path), address=to_address, _id=_id)
    remove(ctx=ctx, address=from_address)


def edit(ctx):
    render.render(ctx=ctx)

    old_state = ctx.terraform_dir.joinpath("old.tfstate")
    helpers.run_script(f"{config.TERRAFORM_PATH} -chdir={ctx.work_dir} state pull > '{old_state}'")  # we use run_script so we can redirect output easily to old_state

    new_state = ctx.terraform_dir.joinpath("new.tfstate")
    helpers.run_command("cp", old_state, new_state)

    helpers.run_command(config.EDITOR, new_state)

    helpers.run_script(f"diff -ru --color {old_state} {new_state} || true")  # '|| true' because diff returns non-zero if differences were found, which would mean we sys.exit and halt execution
    if input("Proceed with changes? [y/N] ").lower().startswith("y"):
        # we do NOT increase serial automatically, to protect non-experts from themselves
        helpers.run_command(config.TERRAFORM_PATH, f"-chdir={ctx.work_dir}", "state", "push", new_state)
