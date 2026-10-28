#!/bin/sh
set -e

export WAIT_HOSTS=$API_HOST:$API_PORT

# Apply environment replacements
envsubst < replacements.sed > replacements_values.sed
sed -i -f replacements_values.sed *.js 2>/dev/null || true

# Generate nginx configuration with proper headers
cat << 'EOF' > /etc/nginx/nginx.conf
user nginx;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  
  log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent "$http_referer" '
                  '"$http_user_agent" "$http_x_forwarded_for"';

  access_log /var/log/nginx/access.log main;

  upstream api {
    server api:3000;
  }

  server {
    listen 4200;
    root /srv/gauzy;

    add_header Access-Control-Allow-Origin * always;

    location ~* \.(js|css|html|json|svg|png)$ {
      add_header Cache-Control "no-cache, no-store, must-revalidate" always;
      add_header Pragma "no-cache" always;
      add_header Expires 0 always;
      try_files $uri =404;
    }

    location ^~ /assets/ {    
      add_header Cache-Control "no-cache, no-store, must-revalidate" always;
      try_files $uri =404;
    }

    location / {
      try_files $uri $uri/ /index.html;      
    }

    location ^~ /api/ {
      proxy_pass http://api;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header CF-Connecting-IP "";
    }
  }
}
EOF

# 1. Copy logo patch
if [ -f /srv/gauzy/patches/logo_Gauzy.svg ]; then
  mkdir -p /srv/gauzy/assets/images/logos
  cp -f /srv/gauzy/patches/logo_Gauzy.svg /srv/gauzy/assets/images/logos/logo_Gauzy.svg
fi

# 1b. Copy Octapus Auth Model and Color System assets
if [ -f /srv/gauzy/patches/octapus-auth-model.css ]; then
  mkdir -p /srv/gauzy/assets
  cp -f /srv/gauzy/patches/octapus-auth-model.css /srv/gauzy/assets/octapus-auth-model.css
fi

if [ -f /srv/gauzy/patches/obms-color-system.css ]; then
  mkdir -p /srv/gauzy/assets
  cp -f /srv/gauzy/patches/obms-color-system.css /srv/gauzy/assets/obms-color-system.css
fi

if [ -f /srv/gauzy/patches/octapus-auth-model.js ]; then
  mkdir -p /srv/gauzy/assets
  cp -f /srv/gauzy/patches/octapus-auth-model.js /srv/gauzy/assets/octapus-auth-model.js
fi

if [ -f /srv/gauzy/patches/auth-hero-asset.jpg ]; then
  mkdir -p /srv/gauzy/assets /srv/gauzy/assets/images
  cp -f /srv/gauzy/patches/auth-hero-asset.jpg /srv/gauzy/assets/auth-hero-asset.jpg
  cp -f /srv/gauzy/patches/auth-hero-asset.jpg /srv/gauzy/assets/images/auth-hero-asset.jpg
  cp -f /srv/gauzy/patches/auth-hero-asset.jpg /srv/gauzy/auth-hero-asset.jpg
fi

# 2. Copy 1404.d530167e5825dfd1.js patch if present
if [ -f /srv/gauzy/patches/1404.d530167e5825dfd1.js ]; then
  cp -f /srv/gauzy/patches/1404.d530167e5825dfd1.js /srv/gauzy/1404.d530167e5825dfd1.js
fi

# 3. Rebrand index.html and manifest.json
if [ -f /srv/gauzy/index.html ]; then
  sed -i 's|<title>.*</title>|<title>OBMS ERP - Powered by Octapus System</title>|g' /srv/gauzy/index.html
  sed -i 's|Gauzy|OBMS ERP|g' /srv/gauzy/index.html
  sed -i 's|Ever Co. LTD|Octapus System|g' /srv/gauzy/index.html 2>/dev/null || true
  if ! grep -q "obms-color-system.css" /srv/gauzy/index.html; then
    sed -i 's|</head>|<link rel="stylesheet" href="assets/obms-color-system.css">\n<link rel="stylesheet" href="assets/octapus-auth-model.css">\n<script src="assets/octapus-auth-model.js" defer></script>\n</head>|g' /srv/gauzy/index.html
  fi
fi

if [ -f /srv/gauzy/manifest.json ]; then
  sed -i 's|"name": "Gauzy"|"name": "OBMS ERP"|g' /srv/gauzy/manifest.json
  sed -i 's|"short_name": "gauzy"|"short_name": "OBMS ERP"|g' /srv/gauzy/manifest.json
fi

# 4. Rebrand i18n JSON files
for f in /srv/gauzy/assets/i18n/*.json; do
  [ -f "$f" ] || continue
  sed -i 's|Ever® Gauzy™|OBMS ERP|g' "$f"
  sed -i 's|Ever Gauzy|OBMS ERP|g' "$f"
  sed -i 's|Ever®|OBMS ERP|g' "$f"
  sed -i 's|Gauzy AI|OBMS ERP AI|g' "$f"
  sed -i 's|Gauzy Platform|OBMS ERP Platform|g' "$f"
  sed -i 's|Gauzy Desktop|OBMS ERP Desktop|g' "$f"
  sed -i 's|Gauzy Server|OBMS ERP Server|g' "$f"
  sed -i 's|Gauzy Timer|OBMS ERP Timer|g' "$f"
  sed -i 's|Gauzy Agent|OBMS ERP Agent|g' "$f"
  sed -i 's|Gauzy|OBMS ERP|g' "$f"
  sed -i 's|gauzy|OBMS ERP|g' "$f"
  sed -i 's|GAUZY|OBMS ERP|g' "$f"
  sed -i 's|Ever Co. LTD|Octapus System|g' "$f"
  sed -i 's|Ever Co. Ltd|Octapus System|g' "$f"
  sed -i 's|Ever Co.|Octapus System|g' "$f"
  sed -i 's|Ever Technologies LTD|Octapus System|g' "$f"
  sed -i 's|Ever Technologies|Octapus System|g' "$f"
  sed -i 's|Ever Works|Octapus System|g' "$f"
  sed -i 's|Ever Async|Octapus System Async|g' "$f"
  sed -i 's|Ever ID|Octapus ID|g' "$f"
  sed -i 's|All rights reserved.|All rights reserved. Powered by Octapus System.|g' "$f"
done

# 5. Patch JS chunks for AED currency, branding, and credentials
for f in /srv/gauzy/*.js; do
  [ -f "$f" ] || continue
  sed -i 's|"Gauzy"|"OBMS ERP"|g' "$f" 2>/dev/null || true
  sed -i "s|'Gauzy'|'OBMS ERP'|g" "$f" 2>/dev/null || true
  sed -i 's|"Ever Gauzy"|"OBMS ERP"|g' "$f" 2>/dev/null || true
  sed -i "s|'Ever Gauzy'|'OBMS ERP'|g" "$f" 2>/dev/null || true
  sed -i 's|"Ever Co. LTD"|"Octapus System"|g' "$f" 2>/dev/null || true
  sed -i "s|'Ever Co. LTD'|'Octapus System'|g" "$f" 2>/dev/null || true
  sed -i 's|"Ever Co."|"Octapus System"|g' "$f" 2>/dev/null || true
  sed -i "s|'Ever Co.'|'Octapus System'|g" "$f" 2>/dev/null || true
  sed -i 's|DEFAULT_CURRENCY:"USD"|DEFAULT_CURRENCY:"AED"|g' "$f" 2>/dev/null || true
  sed -i 's|"DEFAULT_CURRENCY":"USD"|"DEFAULT_CURRENCY":"AED"|g' "$f" 2>/dev/null || true
  sed -i 's|defaultCurrency:"USD"|defaultCurrency:"AED"|g' "$f" 2>/dev/null || true
  sed -i 's|"defaultCurrency":"USD"|"defaultCurrency":"AED"|g' "$f" 2>/dev/null || true
  sed -i 's|currency||"USD"|currency||"AED"|g' "$f" 2>/dev/null || true
  sed -i "s|currency||'USD'|currency||'AED'|g" "$f" 2>/dev/null || true
  sed -i 's|this.defaultCurrency||"USD"|this.defaultCurrency||"AED"|g' "$f" 2>/dev/null || true
  sed -i "s|this.defaultCurrency||'USD'|this.defaultCurrency||'AED'|g" "$f" 2>/dev/null || true
  sed -i 's|"billRateCurrency":"USD"|"billRateCurrency":"AED"|g' "$f" 2>/dev/null || true
  sed -i 's|billRateCurrency:"USD"|billRateCurrency:"AED"|g' "$f" 2>/dev/null || true
  sed -i 's/DEMO_SUPER_ADMIN_PASSWORD:"admin"/DEMO_SUPER_ADMIN_PASSWORD:"admin123"/g' "$f" 2>/dev/null || true
  sed -i 's/DEMO_ADMIN_PASSWORD:"admin"/DEMO_ADMIN_PASSWORD:"admin123"/g' "$f" 2>/dev/null || true
  sed -i 's|You are using a demo account. Finding our software useful?||g' "$f" 2>/dev/null || true
  sed -i 's|Click here to Sign Up and start using for free!||g' "$f" 2>/dev/null || true
done

./wait

exec "$@"
