# git push protection hook
This directory contains a set of git hook scripts which add a manual confirmation step when pushing directly to a protected branch.

This is complicated because `git-lfs` also needs to install custom hook scripts which won't work if another hook script already exists.  The ideal solution would be for git to support multiple pre-push hook scripts, but that feature hasn't been implemented.  The [workaround](https://github.com/git-lfs/git-lfs/issues/2865) is to combine our custom hook with the `git-lfs` hook script.  However not all repos use `git-lfs`, so the `git-lfs` portion needs to be conditional on lfs being enabled.

Installing a single hook script for `pre-commit` prevents all `git-lfs` hook scripts from being installed.  This means that all the other `git-lfs` hook scripts need to be duplicated here with a similar runtime check for lfs being enabled.

## Setup
1. Check if you already have a git templates directory setup with

        git config init.templatedir

1. If you do skip to step 3.  If not, then set one up:

        mkdir -p ~/.git-templates/hooks/
        git config --global init.templatedir ~/.git-templates/

1. Copy these hook scripts to your git template hooks directory:

        cp post-checkout post-commit post-merge pre-push $(git config init.templatedir)/hooks/
        chmod +x $(git config init.templatedir)/hooks/*

Now any new repositories that are cloned or checked out will use the hook scripts from your template directory.
