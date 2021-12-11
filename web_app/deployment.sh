# git clone https://github.com/Lockers13/codagio
# cd codagio
# git checkout portf_deployment
# chmod u+x web_app/deployment.sh
python3 -m venv env; . env/bin/activate
pip3 install wheel; pip3 install -r requirements.txt
echo $PUB_IP
cd web_app
sed -i 's/ALLOWED_HOSTS = []/ALLOWED_HOSTS = [$HOST_IP]/g' app/settings.py
sed -i "s/'USER': 'lorcan'/'USER': 'postgres'/g" app/settings.py
# echo $PUB_IP #! copy-paste
#
# ALLOWED_HOSTS = [$PUB_IP]
# DB_USER => postgres
# DB => sudo -u postgres psql postgres
# python manage.py makemigrations
# python manage.py migrate
for i in $(find static/js -name "*.js"); do sed -i 's/localhost/$HOST_IP/g' "$i"; done
# make sample_tutor superuser

# MAKE REGISTRATION/LOGIN EXPERIENCE BETTER
# LOGIN CREDS: lorcan, cgcexample; sample_tutor, on*************; course: MIT_CS201, sample_course123
