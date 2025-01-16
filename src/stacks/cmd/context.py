import pathlib

from . import config


class Context:
    def __init__(self, path=pathlib.Path().cwd(), out=pathlib.Path().cwd().joinpath(config.OUTPUT_DIR), parent=None):
        if path == path.parent.joinpath(out.name):
            out = path
            path = path.parent
        self.path = path
        self.root_dir = self.path.parent.parent.parent.parent
        self.envs_dir = self.root_dir.joinpath(config.ENVIRONMENTS_DIR)
        self.stacks_dir = self.root_dir.joinpath(config.STACKS_DIR)
        self.stack_dir = self.path.parent.parent
        self.base_dir = self.stack_dir.joinpath(config.BASE_DIR)
        self.work_dir = out
        self.terraform_dir = self.work_dir.joinpath(".terraform")
        self.modules_dir = self.terraform_dir.joinpath("modules")
        self.universe_file = self.work_dir.joinpath("stacks.tf.json")
        self.variables_file = self.work_dir.joinpath("zzz.auto.tfvars.json")  # 'zzz.auto.tfvars.json' so that it has the topmost precedence
        self.stack = self.stack_dir.name
        self.layer = self.path.name
        layer_split = self.layer.split("_", 1)
        env_split = layer_split[0].split("@", 1)
        self.env = env_split[0]
        self.env_dir = self.envs_dir.joinpath(self.env)
        self.subenv = env_split[1] if len(env_split) > 1 else None
        self.subenv_dir = self.env_dir.joinpath(self.subenv) if self.subenv else None
        self.instance = layer_split[1] if len(layer_split) > 1 else None
        assert self.env_dir.exists()
        assert self.subenv_dir is None or self.subenv_dir.exists()
        self.ancestor = parent.ancestor if parent and parent.ancestor else parent
        self.parent = parent
