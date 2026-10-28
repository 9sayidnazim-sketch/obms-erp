#!/bin/bash
set -e
exec > /var/log/user-data.log 2>&1

echo "=== Starting Gauzy EC2 Cloud-Init Deployment ==="
date

# 1. Update and install packages
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release unzip jq netcat-openbsd awscli

# 2. Install Docker & Docker Compose plugin
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

# 3. Create app directory and download deployment bundle from S3
mkdir -p /opt/gauzy
cd /opt/gauzy

echo "Downloading deployment bundle from S3..."
aws s3 cp s3://orbit-deploy-109613847761-20261012/gauzy/gauzy-deploy.tar.gz /tmp/gauzy-deploy.tar.gz --region ap-south-1
tar -xzf /tmp/gauzy-deploy.tar.gz -C /opt/gauzy/
chmod +x api-patch-entrypoint.sh webapp-patch-entrypoint.sh

# 4. Resolve Public IP
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || curl -s http://checkip.amazonaws.com)
echo "Instance Public IP: $PUBLIC_IP"

# 5. Wait for RDS PostgreSQL to become available
RDS_IDENTIFIER="gauzy-db"
AWS_REGION="ap-south-1"

echo "Waiting for RDS instance $RDS_IDENTIFIER to be ready..."
while true; do
  STATUS=$(aws rds describe-db-instances --db-instance-identifier "$RDS_IDENTIFIER" --region "$AWS_REGION" --query "DBInstances[0].DBInstanceStatus" --output text 2>/dev/null || echo "pending")
  echo "Current RDS status: $STATUS"
  if [ "$STATUS" = "available" ]; then
    break
  fi
  sleep 15
done

DB_HOST=$(aws rds describe-db-instances --db-instance-identifier "$RDS_IDENTIFIER" --region "$AWS_REGION" --query "DBInstances[0].Endpoint.Address" --output text)
echo "Resolved RDS Endpoint: $DB_HOST"

# Verify TCP connectivity to PostgreSQL
echo "Testing connectivity to $DB_HOST:5432..."
until nc -z -v -w5 "$DB_HOST" 5432; do
  echo "Waiting for TCP connection to $DB_HOST:5432..."
  sleep 5
done
echo "Postgres port 5432 is open and responsive!"

# 6. Generate .env.prod
cat << EOF > /opt/gauzy/.env.prod
NODE_ENV=production
APP_NAME="OBMS ERP"
COMPANY_NAME="Octapus System"
COMPANY_SITE_NAME="Octapus System"
COMPANY_LINK="https://octapus.system"
DEFAULT_CURRENCY=AED
IS_DOCKER=true
API_HOST=api
API_PORT=3000
WEB_HOST=webapp
WEB_PORT=4200
DEMO=false
ALLOW_SUPER_ADMIN_ROLE=true
ALLOW_INSECURE_SEED_CREDENTIALS=true
API_BASE_URL=http://${PUBLIC_IP}:3000
CLIENT_BASE_URL=http://${PUBLIC_IP}
DB_ORM=typeorm
DB_TYPE=postgres
DB_SYNCHRONIZE=false
DB_HOST=${DB_HOST}
DB_PORT=5432
DB_NAME=gauzy
DB_USER=postgres
DB_PASS=GauzyDatabase2026!
DB_POOL_SIZE=40
DB_POOL_SIZE_KNEX=10
DB_CONNECTION_TIMEOUT=15000
DB_IDLE_TIMEOUT=30000
DB_SLOW_QUERY_LOGGING_TIMEOUT=10000
DB_SSL_MODE=false
REDIS_ENABLED=false
JWT_SECRET=superSecretGauzyKey1234567890123456789012345678901234567890
EXPRESS_SESSION_SECRET=sessionSecretGauzyKey1234567890123456789012345678901234567890
JWT_REFRESH_TOKEN_SECRET=refreshSecretGauzyKey1234567890123456789012345678901234567890
JWT_REFRESH_TOKEN_EXPIRATION_TIME=86400
JWT_VERIFICATION_TOKEN_SECRET=verificationSecretGauzyKey1234567890123456789012345678901234567890
JWT_VERIFICATION_TOKEN_EXPIRATION_TIME=86400
DEMO_SUPER_ADMIN_PASSWORD=admin123
DEMO_ADMIN_PASSWORD=admin123
DEMO_EMPLOYEE_PASSWORD=admin123
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

# 7. Start containers
echo "Starting Gauzy with docker compose..."
docker compose -f docker-compose.prod.yml up -d

echo "=== Deployment Complete at $(date) ==="
echo "Gauzy is available at: http://${PUBLIC_IP}"
