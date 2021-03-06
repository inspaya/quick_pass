#!/usr/bin/env python
# Original concept from
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

import imp

from migrate.versioning import api
from app import db
from config import Config as cfg

db_version = api.db_version(cfg.SQLALCHEMY_DATABASE_URI, cfg.SQLALCHEMY_MIGRATE_REPO)
migration = cfg.SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (db_version + 1))
tmp_module = imp.new_module('old_model')
old_model = api.create_model(cfg.SQLALCHEMY_DATABASE_URI, cfg.SQLALCHEMY_MIGRATE_REPO)
exec(old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(
    cfg.SQLALCHEMY_DATABASE_URI,
    cfg.SQLALCHEMY_MIGRATE_REPO,
    tmp_module.meta,
    db.metadata
)
open(migration, "wt").write(script)
api.upgrade(cfg.SQLALCHEMY_DATABASE_URI, cfg.SQLALCHEMY_MIGRATE_REPO)
new_db_version = api.db_version(cfg.SQLALCHEMY_DATABASE_URI, cfg.SQLALCHEMY_MIGRATE_REPO)
print('New migration saved as ' + migration)
print('Current Database Version ' + str(new_db_version))
