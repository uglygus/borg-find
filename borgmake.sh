#!/bin/sh

REPO="/Users/tbatters/BIG-STUFF/borgrepo_test/repo"

NOW=$(date +"%m-%d-%Y_%M%M%S")

borg init $REPO



borg create $REPO::NOW ~/BIG-STUFF/media-shorts