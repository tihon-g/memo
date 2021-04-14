ssh root@165.232.53.1
cd /home/django/rendering/
git pull origin
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn