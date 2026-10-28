#!/bin/bash
set -e
exec > /var/log/gauzy-install.log 2>&1

echo "=== Starting Gauzy Installation on EC2 ==="
date

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release unzip jq netcat-openbsd

# Install Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

# Configure 4GB Swap
if [ ! -f /swapfile ]; then
  echo "Configuring 4GB Swap..."
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo "/swapfile none swap sw 0 0" >> /etc/fstab
fi

# Install AWS CLI v2
if ! command -v aws &> /dev/null; then
  echo "Installing AWS CLI v2..."
  curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
  unzip -q /tmp/awscliv2.zip -d /tmp/
  /tmp/aws/install
  rm -rf /tmp/aws /tmp/awscliv2.zip
fi

# Download deployment bundle
mkdir -p /opt/gauzy
cd /opt/gauzy

echo "Fetching deployment bundle from S3..."
aws s3 cp s3://orbit-deploy-109613847761-20261012/gauzy/gauzy-deploy.tar.gz /tmp/gauzy-deploy.tar.gz --region ap-south-1
tar -xzf /tmp/gauzy-deploy.tar.gz -C /opt/gauzy/
chmod +x api-patch-entrypoint.sh webapp-patch-entrypoint.sh

# Resolve Public IP
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || curl -s http://checkip.amazonaws.com)
echo "Instance Public IP: $PUBLIC_IP"

# Database Configuration
DB_HOST="gauzy-db.chmeo2uym5py.ap-south-1.rds.amazonaws.com"
DB_PASS="GauzySecurePass2026"
DB_USER="postgres"
DB_NAME="gauzy"

echo "Waiting for RDS Postgres ($DB_HOST:5432)..."
until nc -z -v -w5 "$DB_HOST" 5432; do
  echo "Waiting for RDS Postgres..."
  sleep 5
done
echo "Postgres RDS is ready!"

# Generate .env
cat << EOF > /opt/gauzy/.env
NODE_ENV=production
APP_NAME="OBMS ERP"
COMPANY_NAME="Octapus System"
COMPANY_SITE_NAME="Octapus System"
COMPANY_LINK="https://octapus.system"
DEFAULT_CURRENCY="AED"
APP_SIGNATURE="OBMS ERP Team - Octapus System"
IS_DOCKER=true
API_HOST=api
API_PORT=3000
WEB_HOST=webapp
WEB_PORT=4200
DEMO=true
ALLOW_SUPER_ADMIN_ROLE=true
API_BASE_URL=http://${PUBLIC_IP}:3000
CLIENT_BASE_URL=http://${PUBLIC_IP}
DB_ORM=typeorm
DB_TYPE=postgres
DB_SYNCHRONIZE=false
DB_HOST=${DB_HOST}
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASS=${DB_PASS}
DB_POOL_SIZE=40
DB_POOL_SIZE_KNEX=10
DB_CONNECTION_TIMEOUT=15000
DB_IDLE_TIMEOUT=30000
DB_SLOW_QUERY_LOGGING_TIMEOUT=10000
DB_SSL_MODE=true
REDIS_ENABLED=false
JWT_SECRET=superSecretGauzyKey1234567890123456789012345678901234567890
EXPRESS_SESSION_SECRET=sessionSecretGauzyKey1234567890123456789012345678901234567890
JWT_REFRESH_TOKEN_SECRET=refreshSecretGauzyKey1234567890123456789012345678901234567890
JWT_REFRESH_TOKEN_EXPIRATION_TIME=86400
JWT_VERIFICATION_TOKEN_SECRET=verificationSecretGauzyKey1234567890123456789012345678901234567890
JWT_VERIFICATION_TOKEN_EXPIRATION_TIME=86400
DEMO_SUPER_ADMIN_PASSWORD=admin123
DEMO_ADMIN_PASSWORD=admin123
ALLOWED_ORIGINS=*
FILE_PROVIDER=LOCAL
FEATURE_EMAIL_PASSWORD_LOGIN=true
FEATURE_MAGIC_LOGIN=true
FEATURE_DASHBOARD=true
FEATURE_TIME_TRACKING=true
FEATURE_EMPLOYEES=true
FEATURE_ORGANIZATION=true
FEATURE_CONTACT=true
FEATURE_GOAL=true
FEATURE_REPORT=true
FEATURE_SETTING=true
EOF

# Start Docker containers
echo "Starting Gauzy with docker compose..."
docker compose -f docker-compose.prod.yml up -d

echo "Gauzy Docker containers started!"
docker ps -a
