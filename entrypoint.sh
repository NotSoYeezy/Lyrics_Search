#!/bin/bash
flask db upgrade
exec python web_app/main.py
