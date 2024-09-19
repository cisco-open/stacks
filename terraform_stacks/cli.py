import argparse

from .preinit import main as preinit_main
from .postinit import main as postinit_main


def main():
    """
    The entrypoint when calling `stacks` from the CLI.
    """
    parser = argparse.ArgumentParser(
        prog="stacks",
        description="The Terraform code pre-processor.",
    )
    parser.add_argument(
        "command",
        choices=[
            "preinit",
            "postinit",
        ],
    )
    args = parser.parse_args()

    if args.command == "preinit":
        preinit_main()
    elif args.command == "postinit":
        postinit_main()
