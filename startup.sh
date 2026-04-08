#!/bin/bash
# Azure App Service startup command
# Este archivo se configura en: App Service > Configuration > General Settings > Startup Command
# O Azure lo detecta automáticamente si se llama startup.sh

gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=120 app:app
