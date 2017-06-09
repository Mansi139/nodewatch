#! /bin/bash

pip install virtualenv
virtualenv env

source env/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --name=nodewatchd manage.py -y
cp -r env/lib/python3.5/site-packages/rest_framework/templates/ dist/rest_framework_templates

# Build the .deb file
mkdir -p deb_build/usr/local/bin/
cp -r dist/ deb_build/usr/local/bin/nodewatchd
cp nodewatch.service deb_build/
mkdir deb_build/DEBIAN

echo "Package: nodewatch" >> deb_build/DEBIAN/control
echo "Maintainer: nodewatch" >> deb_build/DEBIAN/control
echo "Description: nodewatch" >> deb_build/DEBIAN/control
echo "Version: 0.0.0" >> deb_build/DEBIAN/control
echo "Architecture: armhf" >> deb_build/DEBIAN/control

echo "mv nodewatch.service /etc/systemd/system/" >> deb_build/DEBIAN/postinst
echo "systemctl start nodewatch" >> deb_build/DEBIAN/postinst

chmod 775 deb_build/DEBIAN/postinst

mv deb_build/ nodewatchd/
dpkg-deb --build nodewatchd

# Clean up
rm nodewatchd.spec
rm -rf build/ dist/ nodewatchd/
