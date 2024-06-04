#!/bin/sh

REPO="/Users/tbatters/BIG-STUFF/borgrepo_test/repo"
REPO_BACKUP=$REPO-backup

cp -r $REPO $REPO_BACKUP

#borg info --json  $REPO

echo orig-repo=
borg list --short $REPO

borg recreate  --verbose  --exclude ".DS_Store" $REPO:

# borg list --short $REPO | while read ARCHIVE
# do
#     echo
#     echo ARCHIVE=$ARCHIVE
#     borg recreate  --verbose  --exclude ".DS_Store" $REPO::$ARCHIVE 
#     echo borg recreate  --verbose  --exclude ".DS_Store" $REPO::$ARCHIVE 

#     echo borg recreate done.
#     echo
# done


echo new-repo=
borg list --short $REPO



du -s $REPO 
du -s $REPO_BACKUP

borg compact $REPO

du -s $REPO 
du -s $REPO_BACKUP

