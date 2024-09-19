import subprocess
from pytest_dir_equal import assert_dir_equal


def test_legacy_invocation_still_works():
    # create the stacks.out directory using the legacy invocation pattern
    subprocess.run(
        ["python ../../../../../terraform_stacks/preinit.py"],
        cwd="example/stacks/example/layers/staging",
        shell=True,
    ).check_returncode()
    subprocess.run(
        ["python ../../../../../terraform_stacks/preinit.py"],
        cwd="example/stacks/example/layers/production",
        shell=True,
    ).check_returncode()

    assert_dir_equal(
        "example/stacks/example/layers/staging/stacks.out",
        "tests/example/stacks/example/layers/staging/stacks.out",
    )
    assert_dir_equal(
        "example/stacks/example/layers/production/stacks.out",
        "tests/example/stacks/example/layers/production/stacks.out",
    )
