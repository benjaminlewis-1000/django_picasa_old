#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source $THIS_DIR/.env_laptop

mkdir -p $TAGGER_META_DIR
mkdir -p $TAGGER_META_DIR/django_photos
mkdir -p $TAGGER_META_DIR/thumbnails
mkdir -p $TAGGER_DB_DIR
mkdir -p $TAGGER_DB_DIR/database
mkdir -p $TAGGER_DB_DIR/rabbit


