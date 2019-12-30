#!/usr/bin/env python

# reference build https://travis-ci.org/louiscklaw/test_git_repo/builds/625335510
# https://docs.travis-ci.com/user/environment-variables/

import os, re, subprocess
import slack

from fabric.api import local, shell_env, lcd, run, settings


BRANCH_TO_MERGE_INTO='develop'
BRANCH_TO_MERGE_REGEX='^feature'

BUILDKITE_PIPELINE_SLUG = os.environ['BUILDKITE_PIPELINE_SLUG']
BUILDKITE_BRANCH = os.environ['BUILDKITE_BRANCH']
BUILDKITE_BUILD_NUMBER = os.environ['BUILDKITE_BUILD_NUMBER']
BUILDKITE_COMMIT = os.environ['BUILDKITE_COMMIT']

GITHUB_TOKEN = "os.environ['GITHUB_TOKEN']"

PUSH_URI="https://{}@github.com/{}".format(GITHUB_TOKEN, BUILDKITE_PIPELINE_SLUG)


def run_command(command_body):
  command_result = local(command_body, capture=True)
  print(command_result)
  return command_result

m = re.match(BRANCH_TO_MERGE_REGEX, BUILDKITE_BRANCH)
if (m == None ) :
  print('skipping merge for branch {}'.format(BUILDKITE_BRANCH))
  slack_message('skip merging for BUILD #{} `{}` from `{}` to `{}`'.format(BUILDKITE_BUILD_NUMBER, BUILDKITE_PIPELINE_SLUG, BUILDKITE_BRANCH, BRANCH_TO_MERGE_INTO), '#travis-build-result')
else:
  with lcd(TEMP_DIR), settings(warn_only=True):
    print('checkout {} branch'.format(BRANCH_TO_MERGE_INTO))
    run_command('git checkout {}'.format(BRANCH_TO_MERGE_INTO))

    print('Merging "{}"'.format(BUILDKITE_COMMIT))
    result_to_check = run_command('git merge --ff-only "{}"'.format(BUILDKITE_COMMIT))

    if result_to_check.failed:
      slack_message('error found during merging BUILD{} `{}` from `{}` to `{}`'.format(BUILDKITE_BUILD_NUMBER, BUILDKITE_PIPELINE_SLUG, BUILDKITE_BRANCH, BRANCH_TO_MERGE_INTO), '#travis-build-result')
    else:
      slack_message('merging BUILD{} from {} `{}` to `{}` done'.format(BUILDKITE_BUILD_NUMBER, BUILDKITE_PIPELINE_SLUG, BUILDKITE_BRANCH, BRANCH_TO_MERGE_INTO), '#travis-build-result')

    print('push commit')
    run_command("git push {} {}".format(PUSH_URI, BRANCH_TO_MERGE_INTO))
