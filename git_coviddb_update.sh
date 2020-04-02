#!/bin/bash
REPO_DIR=/home/pi/korona/czech-covid-db/
COMMIT_MSG="Automated parse from wikipedia/MZCR UZIS"
LOCAL_BRANCH=master
REMOTE_NAME=origin

cd $REPO_DIR
git add .
git commit -m "$COMMIT_MSG"
git push $REMOTE_NAME $LOCAL_BRANCH
