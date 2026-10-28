#!/bin/bash
set -e
echo "=== DEPLOYING OCTAPUS AUTH MODEL ON EC2 ==="

cd /opt/gauzy
aws s3 cp s3://orbit-deploy-109613847761-20261012/gauzy/gauzy-deploy.tar.gz /opt/gauzy/gauzy-deploy.tar.gz --region ap-south-1
tar -xzf /opt/gauzy/gauzy-deploy.tar.gz -C /opt/gauzy/
chmod +x /opt/gauzy/*.sh

echo "Extracted files in /opt/gauzy:"
ls -la /opt/gauzy/octapus* /opt/gauzy/logo*

# Run python rebrand script
python3 /opt/gauzy/rebrand_webapp.py

# Directly copy octapus auth model and obms color system into webapp container
docker cp /opt/gauzy/octapus-auth-model.css webapp:/srv/gauzy/assets/octapus-auth-model.css
docker cp /opt/gauzy/obms-color-system.css webapp:/srv/gauzy/assets/obms-color-system.css
docker cp /opt/gauzy/octapus-auth-model.js webapp:/srv/gauzy/assets/octapus-auth-model.js
docker cp /opt/gauzy/auth-hero-asset.jpg webapp:/srv/gauzy/assets/auth-hero-asset.jpg 2>/dev/null || true
docker cp /opt/gauzy/auth-hero-asset.jpg webapp:/srv/gauzy/auth-hero-asset.jpg 2>/dev/null || true

# Ensure index.html has the links
docker exec webapp sh -c "
if ! grep -q 'obms-color-system.css' /srv/gauzy/index.html; then
  sed -i 's|</head>|<link rel=\"stylesheet\" href=\"assets/obms-color-system.css\">\n<link rel=\"stylesheet\" href=\"assets/octapus-auth-model.css\">\n<script src=\"assets/octapus-auth-model.js\" defer></script>\n</head>|g' /srv/gauzy/index.html
fi
"

# Restart containers with fresh compose
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

echo "=== DEPLOY COMPLETED SUCCESSFULLY ==="
