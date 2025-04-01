import shutil

from .. import helpers


def preinit(ctx):
    helpers.directory_remove(ctx.work_dir, keep=[".terraform", ".terraform.lock.hcl"])

    variables_predefined = {
        "stacks_path": f"stacks/{ctx.stack}/layer/{ctx.layer}",
        "stacks_root": "/".join([".."] * (len(ctx.work_dir.parts) - len(ctx.root_dir.parts))),
        "stacks_stack": ctx.stack,
        "stacks_layer": ctx.layer,
        "stacks_environment": ctx.env,
        "stacks_subenvironment": ctx.subenv or "",
        "stacks_instance": ctx.instance or "",
        "stacks_environments": {
            item.name: helpers.hcl2_read([item.joinpath("env.tfvars")])  # TODO: replace 'env.tfvars' with '*.tfvars' after all stacks have been upgraded to v2
            for item in ctx.envs_dir.iterdir()
            if item.is_dir() and item.joinpath("env.tfvars").exists()
        },
    }

    helpers.copy_files(ctx.stacks_dir, ctx.work_dir, include=["*.tf", "*.tfvars.jinja"], prefix="common_")
    helpers.copy_files(ctx.stack_dir, ctx.work_dir, include=["*.tfvars.jinja"], prefix="stack_")
    for item in ctx.base_dir.iterdir():
        destination = ctx.work_dir.joinpath(item.name)
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        elif item.is_file() and not item.match("*.tf"):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, destination)
    helpers.copy_files(ctx.base_dir, ctx.work_dir, include=["*.tf"], prefix="base_")
    helpers.copy_files(ctx.path, ctx.work_dir, include=["*.tfvars.jinja"], prefix="layer_")

    helpers.jinja2_render(
        ctx=ctx,
        patterns=[ctx.work_dir.joinpath("*.tfvars.jinja")],
        data={
            "var": {
                **helpers.hcl2_read(
                    [
                        pattern
                        for pattern in [
                            ctx.env_dir.joinpath("env.tfvars"),
                            ctx.subenv_dir.joinpath("*.tfvars") if ctx.subenv_dir else None,
                            ctx.stacks_dir.joinpath("*.tfvars"),
                            ctx.stack_dir.joinpath("*.tfvars"),
                            ctx.path.joinpath("*.tfvars"),
                        ]
                        if pattern
                    ]
                ),
                **variables_predefined,
            }
        },
    )

    variables = {
        **helpers.hcl2_read(
            [
                pattern
                for pattern in [
                    ctx.env_dir.joinpath("env.tfvars"),
                    ctx.subenv_dir.joinpath("*.tfvars") if ctx.subenv_dir else None,
                    ctx.stacks_dir.joinpath("*.tfvars"),
                    ctx.work_dir.joinpath("common_*.tfvars.jinja"),
                    ctx.stack_dir.joinpath("*.tfvars"),
                    ctx.work_dir.joinpath("stack_*.tfvars.jinja"),
                    ctx.path.joinpath("*.tfvars"),
                    ctx.work_dir.joinpath("layer_*.tfvars.jinja"),
                ]
                if pattern
            ]
        ),
        **variables_predefined,
    }
    helpers.jinja2_render(
        ctx=ctx,
        patterns=[ctx.work_dir.joinpath("*.tf")],
        data={"var": variables},
    )

    variables_declared = [list(variable.keys())[0] for variable in helpers.hcl2_read([ctx.work_dir.joinpath("*.tf")]).get("variable", [])]

    helpers.json_write(
        {
            "variable": {
                variable: {}
                for variable in {
                    **variables,
                    **helpers.hcl2_read([ctx.work_dir.joinpath("*.auto.tfvars")]),
                }
                if variable not in variables_declared
            }
        },
        ctx.universe_file,
    )

    helpers.json_write(variables, ctx.variables_file)
