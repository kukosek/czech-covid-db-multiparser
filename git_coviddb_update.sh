#!/bin/bash
REPO_DIR=/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/
COMMIT_MSG="Automated parse from wikipedia"
LOCAL_BRANCH=master
REMOTE_NAME=origin

cd $REPO_DIR
git add .
git commit -m "$COMMIT_MSG"
git push $REMOTE_NAME $LOCAL_BRANCH