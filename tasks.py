import os
import shlex
import sys

from invoke import task, util


in_ci = os.environ.get("CI", "false") == "true"
if in_ci:
    pty = False
else:
    pty = util.isatty(sys.stdout) and util.isatty(sys.stderr)


@task
def reformat(c):
    c.run("isort dreg_client tests setup.py tasks.py docker-registry-show.py", pty=pty)
    c.run("black dreg_client tests setup.py tasks.py docker-registry-show.py", pty=pty)


@task
def lint(c):
    c.run("flake8 --show-source --statistics dreg_client tests docker-registry-show.py", pty=pty)
    c.run("check-manifest", pty=pty)


@task
def test(c, onefile=""):
    pytest_args = [
        "pytest",
        "--strict-config",
        "--cov=dreg_client",
        "--cov-report=term-missing",
    ]
    if in_ci:
        pytest_args.extend(("--cov-report-xml", "--strict-markers"))
    else:
        pytest_args.append("--cov-report=html")

    if onefile:
        pytest_args.append(shlex.quote(onefile))

    c.run(" ".join(pytest_args), pty=pty)