#!/usr/bin/env sh
set -eu

git init
git add .
git status --short
printf '\nRepository initialized and staged. Review before committing.\n'
