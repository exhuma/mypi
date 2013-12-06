#!/bin/bash

# Post installation script (example)

alembic -c ${alembic_config} upgrade head
echo "database created"
