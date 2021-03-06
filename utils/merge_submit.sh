#!/bin/bash
# Script that merges a code review and submits it to origin.

EXIT_FAILURE=1;
EXIT_MISSING_ARGS=2;
EXIT_SUCCESS=0;

SCRIPTNAME=`basename $0`;

CL_NUMBER="";

if ! test -f "utils/common.sh";
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

if ! have_curl;
then
  echo "You'll need to install curl for this script to continue.";

  exit ${EXIT_FAILURE};
fi

# Determine if we have the master repo as origin.
HAVE_REMOTE_ORIGIN=have_remote_origin;

if test $# -ne 3;
then
  echo "Usage: ./${SCRIPTNAME} CL_NUMBER USERNAME BRANCH";
  echo "";
  echo "  CL_NUMBER: change list (CL) number that is to be merged and"
  echo "             submitted.";
  echo "  USERNAME: the username of the pull request.";
  echo "  BRANCH: the branch of the pull request.";
  echo "";

  exit ${EXIT_MISSING_ARGS};
fi

CL_NUMBER=$1;
USERNAME=$2;
BRANCH=$3;

GITHUB_URL="https://github.com/${USERNAME}/dfvfs.git";

if ! ${HAVE_REMOTE_ORIGIN};
then
  echo "Submit aborted - invalid origin";

  exit ${EXIT_FAILURE};

fi

if ! have_master_branch;
then
  echo "Submit aborted - current branch is not master.";

  exit ${EXIT_FAILURE};
fi

if have_uncommitted_changes;
then
  echo "Submit aborted - detected uncommitted changes.";

  exit ${EXIT_FAILURE};
fi

if ! local_repo_in_sync_with_origin;
then
  echo "Local repo out of sync with origin: running 'git pull origin master'.":
  git pull origin master

  if test $? -ne 0;
  then
    echo "Submit aborted - unable to run: 'git pull origin master'.";

    exit ${EXIT_FAILURE};
  fi
fi

git pull --squash ${GITHUB_URL} ${BRANCH}

if test $? -ne 0;
then
  echo "Submit aborted - unable to 'git pull ${GITHUB_URL} ${BRANCH}'.";

  exit ${EXIT_FAILURE};
fi

if ! linting_is_correct;
then
  echo "Submit aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

if ! tests_pass;
then
  echo "Submit aborted - fix the issues reported by the failing test.";

  exit ${EXIT_FAILURE};
fi

URL_CODEREVIEW="https://codereview.appspot.com";

# Get the description of the change list.

# This will convert newlines into spaces.
CODEREVIEW=`curl -s ${URL_CODEREVIEW}/api/${CL_NUMBER}`;

DESCRIPTION=`echo ${CODEREVIEW} | sed 's/^.*"subject":"\(.*\)","created.*$/\1/'`;

if test -z "${DESCRIPTION}" || test "${DESCRIPTION}" = "${CODEREVIEW}";
then
  echo "Submit aborted - unable to find change list with number: ${CL_NUMBER}.";

  exit ${EXIT_FAILURE};
fi

EMAIL_ADDRESS=`echo ${CODEREVIEW} | sed 's/^.*"owner_email":"\(.*\)","private.*$/\1/'`;

if test -z "${EMAIL_ADDRESS}" || test "${EMAIL_ADDRESS}" = "${CODEREVIEW}";
then
  echo "Submit aborted - unable to determine author's email address.";

  exit ${EXIT_FAILURE};
fi

# This will convert newlines into spaces.
GITHUB_USERINFO=`curl -s https://api.github.com/users/${USERNAME}`;

FULLNAME=`echo ${GITHUB_USERINFO} | sed 's/^.*"name":"\(.*\)","company*$/\1/'`;

if test -z "${FULLNAME}" || test "${FULLNAME}" = "${GITHUB_USERINFO}";
then
  echo "Submit aborted - unable to determine author's full name";

  exit ${EXIT_FAILURE};
fi

COMMIT_DESCRIPTION="Code review: ${CL_NUMBER}: ${DESCRIPTION}";
AUTHOR="${FULLNAME} <${EMAIL_ADDRESS}>";

echo "Submitting ${COMMIT_DESCRIPTION}";

if test -f "utils/update_version.sh";
then
  . utils/update_version.sh
fi

git commit -a --author="${AUTHOR}" -m "${COMMIT_DESCRIPTION}";

git push

if test $? -ne 0;
then
  echo "Submit aborted - unable to run: 'git push'.";

  exit ${EXIT_FAILURE};
fi

exit ${EXIT_SUCCESS};
