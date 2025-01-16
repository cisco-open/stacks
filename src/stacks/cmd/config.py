import os


ENVIRONMENTS_DIR = os.getenv("STACKS_ENVIRONMENTS_DIR", "environments")
STACKS_DIR = os.getenv("STACKS_STACKS_DIR", "stacks")
BASE_DIR = os.getenv("STACKS_BASE_DIR", "base")
LAYERS_DIR = os.getenv("STACKS_LAYERS_DIR", "layers")
OUTPUT_DIR = os.getenv("STACKS_OUTPUT_DIR", "stacks.out")
TERRAFORM_PATH = os.getenv("STACKS_TERRAFORM_PATH", "terraform")
EDITOR = os.getenv("STACKS_EDITOR", os.getenv("EDITOR", "vi"))
