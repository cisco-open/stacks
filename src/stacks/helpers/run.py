import subprocess
import sys


def run_command(*argv, interactive=True):
    try:
        p = subprocess.run(args=argv, encoding="utf-8", check=True, capture_output=not interactive)
    except subprocess.CalledProcessError as e:
        if interactive:
            sys.exit(e.returncode)
        raise e
    return p


def run_script(script):
    return run_command("bash", "-c", script)
