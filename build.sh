#! /bin/bash

source env/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --name=nodewatchd manage.py -y
cp -r env/lib/python3.5/site-packages/rest_framework/templates/ dist/rest_framework_templates
