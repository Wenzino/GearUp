#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply new database entries
python manage.py makemigrations

# Apply any outstanding database migrations
python manage.py migrate --fake core 0002_remove_brand_logo_remove_feature_icon_brand_image_and_more
