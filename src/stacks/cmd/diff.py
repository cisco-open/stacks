import git

from . import render
from . import context
from .. import helpers


def diff(ctx):
    repository = git.Repo(path=ctx.path, search_parent_directories=True)
    repository.git.stash()

    ctx_old = context.Context(path=ctx.path, out=ctx.work_dir.parent.joinpath(f"{ctx.work_dir.name}.old"))
    render.render(ctx=ctx_old)

    repository.git.stash("pop")

    ctx_new = context.Context(path=ctx.path, out=ctx.work_dir.parent.joinpath(f"{ctx.work_dir.name}.new"))
    render.render(ctx=ctx_new)

    helpers.run_command("diff", "-ur", "--color", ctx_old.work_dir, ctx_new.work_dir)
    helpers.run_command("rm", "-rf", ctx_old.work_dir, ctx_new.work_dir)
