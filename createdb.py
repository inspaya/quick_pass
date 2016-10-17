#!/usr/bin/env python
from os import path
from migrate.versioning import api
from config import Config as cfg
from app import db

db.create_all()

if not path.exists(cfg.SQLALCHEMY_MIGRATE_REPO):
    api.create(cfg.SQLALCHEMY_MIGRATE_REPO, 'Database Migrations')
    api.version_control(cfg.SQLALCHEMY_DATABASE_URI, cfg.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(
        cfg.SQLALCHEMY_DATABASE_URI,
        cfg.SQLALCHEMY_MIGRATE_REPO,
        api.version(cfg.SQLALCHEMY_MIGRATE_REPO)
    )
