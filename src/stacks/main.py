import importlib.metadata
import pathlib
import platform

import click

from . import cmd
from . import helpers


@click.group()
def cli():
    """
    Stacks, the Terraform code pre-processor.

    All commands MUST run within a layer directory, unless noted otherwise.
    """
    pass


@cli.command()
def version():
    print(f"Stacks {importlib.metadata.version('stacks')}")
    print(f"Python {platform.python_version()}")
    terraform_output = helpers.run_command(cmd.config.TERRAFORM_PATH, "version", interactive=False)
    print(f"Terraform {terraform_output.stdout.split('\n')[0].split(' ')[1][1:]}")


@cli.command(hidden=True)  # hidden because it should not be used independently unless for advanced debugging purposes
def preinit():
    cmd.preinit(ctx=cmd.Context())


@cli.command()
@click.option("--init", default="auto", help="Run terraform init (auto, always, never)")
def render(init):
    """
    Render a layer into working Terraform code.
    """
    cmd.render(ctx=cmd.Context(), init=init)


@cli.command()
def diff():
    """
    Render and compare Git HEAD vs current uncommitted changes.
    """
    cmd.diff(ctx=cmd.Context())


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("--init", default="auto", help="Run terraform init (auto, always, never)")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def terraform(init, args):
    """
    Terraform command wrapper.
    """
    cmd.terraform(ctx=cmd.Context(), init=init, args=args)


@cli.command(hidden=True)  # hidden because the key pair is always the same
@click.option("--public-key-path", required=True)
@click.option("--private-key-path", required=True)
def genkey(public_key_path, private_key_path):
    helpers.genkey(public_key_path=pathlib.Path(public_key_path), private_key_path=pathlib.Path(private_key_path))


@cli.command()
@click.option("--public-key-path", required=True)
@click.argument("string")
def encrypt(public_key_path, string):
    """
    Encrypt a secret string using a public key.
    Can run in any directory.
    """
    print(helpers.encrypt(public_key_path=pathlib.Path(public_key_path), string=string))


@cli.command()
@click.option("--private-key-path", required=True)
@click.argument("string")
def decrypt(private_key_path, string):
    """
    Decrypt an encrypted string using a private key.
    Can run in any directory.
    """
    print(helpers.decrypt(private_key_path=pathlib.Path(private_key_path), data=string))


@cli.group()
def surgery():
    """
    Terraform state surgery utilities.
    """
    pass


@surgery.command("edit")
def surgery_edit():
    """
    Edit state with vi.
    """
    cmd.surgery.edit(ctx=cmd.Context())


@surgery.command("list")
def surgery_list():
    """
    List all resources in state by address.
    """
    cmd.surgery._list(ctx=cmd.Context())


@surgery.command("import")
@click.argument("address", required=True)
@click.argument("resource", required=True)
def surgery_import(address, resource):
    """
    Import a resource into state by id.
    """
    cmd.surgery._import(ctx=cmd.Context(), address=address, _id=resource)


@surgery.command("remove")
@click.argument("address", required=True)
def surgery_remove(address):
    """
    Remove a resource from state by address.
    """
    cmd.surgery.remove(ctx=cmd.Context(), address=address)


@surgery.command("move")
@click.argument("from_address", required=True)
@click.argument("to_address", required=True)
@click.argument("to_path", required=True)
def surgery_move(from_address, to_address, to_path):
    """
    Move a resource from one state to another by address.
    """
    ctx = cmd.Context()
    cmd.surgery.move(ctx=ctx, from_address=from_address, to_address=to_address, to_path=ctx.root_dir.joinpath(to_path))


@surgery.command("rename")
@click.argument("from_address", required=True)
@click.argument("to_address", required=True)
def surgery_rename(from_address, to_address):
    """
    Rename a resource in the current state.
    """
    ctx = cmd.Context()
    cmd.surgery.move(ctx=ctx, from_address=from_address, to_address=to_address, to_path=ctx.path)
