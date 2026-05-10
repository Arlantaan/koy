#!/bin/bash
set -e
sudo -u postgres psql -c "ALTER USER koya WITH PASSWORD 'pU03S2bShaCdlyPH0b4xdEJgKoKOjhj1';"
systemctl restart koya
sleep 3
systemctl is-active koya
curl -s -w '\nHTTP:%{http_code}' http://127.0.0.1:8000/api/menu | tail -1
