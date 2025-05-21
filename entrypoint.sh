#!/bin/bash
flask db upgrade --directory "web_app/migrations"

service ssh start
exec gunicorn --bind 0.0.0.0:5000 "web_app.main:create_app()"
