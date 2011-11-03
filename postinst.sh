#!/bin/bash

# Post installation script (example)

python manage manage.py --repository=db_repo --url=sqlite:///app.db
python manage.py version_control
echo "manage.py script created"
