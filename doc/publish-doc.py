"""
build and publish the documentation to GitHub

we build the documentation and copy it to the gh-pages branch using git worktree.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

THISDIR = Path(__file__).parent
ROOTDIR = THISDIR.parent

SRCDIR = THISDIR / "source"
BUILDIR = THISDIR / "build"
HTMLDIR = BUILDIR / "html"  # generated by sphinx

NOJEKYLLFILE = HTMLDIR / ".nojekyll"


def gitget(command: list[str], cwd: Path) -> str:
    out = subprocess.check_output(["git"] + command, cwd=cwd, text=True)
    out = out.rstrip("\n").rstrip(" ")
    return out


def main():
    git_status = gitget(["status", "--porcelain"], cwd=ROOTDIR)
    git_last_commit = gitget(["rev-parse", "HEAD"], cwd=ROOTDIR)
    git_current_branch = gitget(["branch", "--show-current"], cwd=ROOTDIR)
    git_remote_status = gitget(["status", "--short", "--b", "--porcelain"], cwd=ROOTDIR)
    git_ghpages_exists = gitget(["rev-parse", "--verify", "gh-pages"], cwd=ROOTDIR)

    if git_status:
        raise RuntimeError(f"Uncommited changes found: {git_status}.")

    if git_current_branch != "main":
        raise RuntimeError(
            f"current git branch is `{git_current_branch}`, expected `main`."
        )

    if not git_ghpages_exists:
        raise RuntimeError("Branch gh-pages doesn't exists. Create it first.")

    if re.search(rf"## {git_current_branch}.+\[ahead", git_remote_status):
        raise RuntimeError("current git branch is ahead of its remote.")

    if re.search(rf"## {git_current_branch}.+\[behind", git_remote_status):
        raise RuntimeError("current git branch is behind of its remote. ")

    commit_msg = (
        f"chore(doc): sphinx build copied to gh-pages\n\n"
        f"from commit {git_last_commit} on branch {git_current_branch}"
    )

    shutil.rmtree(BUILDIR)
    subprocess.check_call(
        ["git", "worktree", "add", str(HTMLDIR), "gh-pages"], cwd=ROOTDIR
    )
    try:
        # ensure to start clean at each build
        subprocess.check_call(
            ["git", "rm", "--quiet", "--ignore-unmatch", "-r", "*"], cwd=HTMLDIR
        )
        print("calling sphinx-build ...")
        subprocess.check_call(
            [
                "sphinx-build",
                "-M",
                "html",
                str(SRCDIR),
                str(BUILDIR),
            ]
            + sys.argv[1:],
            cwd=THISDIR,
        )

        # necessary for GitHub to use the appropriate build system
        if not NOJEKYLLFILE.exists():
            NOJEKYLLFILE.write_text("")

        subprocess.check_call(["git", "add", "--all"], cwd=HTMLDIR)

        changes = gitget(["status", "--porcelain"], cwd=HTMLDIR)
        if not changes:
            print("nothing to commit, returning ...")
            return

        print(f"changes:\n{'='*8}")
        print(changes)

        subprocess.check_call(["git", "commit", "-m", commit_msg], cwd=HTMLDIR)
        subprocess.check_call(["git", "push", "origin", "gh-pages"], cwd=HTMLDIR)
    finally:
        # ``git worktree remove`` is supposed to delete it but fail, so we do it in python
        shutil.rmtree(HTMLDIR, ignore_errors=True)
        subprocess.check_call(["git", "worktree", "prune"], cwd=ROOTDIR)


if __name__ == "__main__":
    main()
