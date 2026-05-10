#!/bin/bash
set -e

# Fix gzip in nginx.conf
sed -i 's/# gzip_vary on;/gzip_vary on;/' /etc/nginx/nginx.conf
sed -i 's/# gzip_proxied any;/gzip_proxied any;/' /etc/nginx/nginx.conf
sed -i 's/# gzip_comp_level 6;/gzip_comp_level 6;/' /etc/nginx/nginx.conf
sed -i 's/# gzip_buffers 16 8k;/gzip_buffers 16 8k;/' /etc/nginx/nginx.conf
sed -i 's/# gzip_http_version 1.1;/gzip_http_version 1.1;/' /etc/nginx/nginx.conf
sed -i 's|# gzip_types .*|gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml font/woff2 font/woff;|' /etc/nginx/nginx.conf

# Enable HTTP/2
sed -i 's/listen 443 ssl;/listen 443 ssl http2;/' /etc/nginx/sites-enabled/koya

# Test and reload
nginx -t && systemctl reload nginx && echo "ALL OK"
