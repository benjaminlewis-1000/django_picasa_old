#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source $THIS_DIR/.env_laptop
rm -rf $TAGGER_DB_DIR

mkdir -p $TAGGER_META_DIR
mkdir -p $TAGGER_META_DIR/django_photos
mkdir -p $TAGGER_META_DIR/thumbnails
mkdir -p $TAGGER_DB_DIR
mkdir -p $TAGGER_DB_DIR/database
mkdir -p $TAGGER_DB_DIR/rabbit

cp -R $THIS_DIR/test_imgs/* $TAGGER_META_DIR/django_photos

sudo chown -R 1000:1000 $TAGGER_META_DIR
sudo chown -R 1000:1000 $TAGGER_DB_DIR
chmod 777 $TAGGER_DB_DIR/rabbit
touch $TAGGER_DB_DIR/rabbit/enabled_plugins
touch $TAGGER_DB_DIR/rabbit/rabbitmq.conf
