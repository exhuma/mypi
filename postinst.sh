#!/bin/bash

# Post installation script (example)

migrate manage manage.py --repository=db_repo --url=$DATABASE_URL
python manage.py version_control
python manage.py upgrade
echo "database created"
