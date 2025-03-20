# Nginx Reverse Proxy with Self-Signed SSL Certificate

A simple Docker setup for running an Nginx reverse proxy with a self-signed SSL certificate.

This repository provides a ready-to-use configuration for quickly setting up an Nginx reverse proxy with HTTPS support using self-signed certificates. It's perfect for development environments or testing applications that require HTTPS.

## Contents

- `docker-compose.yaml` - Docker Compose configuration for running the Nginx proxy
- `docker-ssl-proxy/` - Directory containing SSL certificates and Nginx configuration
  - `default.conf` - Pre-configured Nginx configuration file -> Edit to match your backend
  - SSL certificate files (pre-generated)
- `recreate-certificate.sh` - Script for regenerating self-signed certificates

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Download the relevant files from this repostiry
   ```
   https://github.com/ezaton/scripts/tree/main/nginx-ssl-proxy
   ```

2. Edit the file docker-ssl-proxy/default.conf to point at your docker backend

3. Start the Nginx proxy:
   ```
   docker-compose up -d
   ```

4. Access your service via HTTPS:
   ```
   https://localhost
   ```
   
   Note: Since this uses a self-signed certificate, your browser will show a security warning. 
   You'll need to accept the certificate exception to proceed.

## Docker Compose Configuration

The `docker-compose.yaml` file included with this repo

## SSL Certificate Information

This repository includes pre-generated self-signed certificates in the `docker-ssl-proxy/ssl/` directory. For security reasons, **you should regenerate these certificates** before using in any environment.

### Regenerating Certificates

Use the included script to recreate your self-signed certificates:

```bash
./recreate-certificate.sh
```

The script will:
1. Create a new private key
2. Generate a new self-signed certificate valid for 36500 days
3. Place the files in the current directory.

## Nginx Configuration

The `docker-ssl-proxy/default.conf` file contains a pre-configured Nginx setup that:

1. Redirects all HTTP traffic to HTTPS
2. Sets up the SSL configuration with appropriate security settings
3. Configures a reverse proxy to forward requests to your application

The main parts of the configuration are:

## Testing the Setup

After starting the containers, you can test the SSL setup using:

```bash
curl -k https://localhost
```

The `-k` flag tells curl to ignore SSL certificate validation errors.

## Production Use

For production environments, consider the following:

- Replace self-signed certificates with proper certificates from a trusted CA
- Use Let's Encrypt for free, trusted certificates
- Strengthen SSL configuration based on your security requirements

## Credits

This configuration is based on the example provided at: https://gist.github.com/ykarikos/06879cbb0d80828fe96445b504fa5b60
