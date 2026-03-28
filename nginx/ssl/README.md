# Nginx SSL Certificate Placeholder
# 
# For production, obtain SSL certificates using Let's Encrypt:
# 
# 1. Install certbot:
#    docker run --rm -it -v ./nginx/ssl:/etc/letsencrypt certbot/certbot certonly --webroot
#
# 2. Place certificates in nginx/ssl/:
#    - cert.pem (fullchain.pem from Let's Encrypt)
#    - key.pem (privkey.pem from Let's Encrypt)
#
# 3. Or copy existing certificates:
#    cp /path/to/fullchain.pem nginx/ssl/cert.pem
#    cp /path/to/privkey.pem nginx/ssl/key.pem
#
# For development/testing, you can generate self-signed certificates:
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#   -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
#   -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Portfolio/CN=localhost"
