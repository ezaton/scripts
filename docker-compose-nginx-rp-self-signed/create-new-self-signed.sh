#!/bin/bash
# will create the resulting self-signed certificates in the current directory
openssl req -subj '/CN=myhost.local' -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 36500
