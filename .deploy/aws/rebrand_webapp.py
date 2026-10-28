import os
import re
import json
import glob
import subprocess

print("=== STARTING OBMS ERP REBRANDING SCRIPT ===")

# 1. Generate PNG logos from SVG using rsvg-convert if available
svg_logo = "/opt/gauzy/logo_Gauzy.svg"
if os.path.exists(svg_logo):
    try:
        subprocess.run(["rsvg-convert", "-w", "180", "-h", "36", svg_logo, "-o", "/opt/gauzy/logo_Gauzy.png"], check=True)
        subprocess.run(["rsvg-convert", "-w", "360", "-h", "72", svg_logo, "-o", "/opt/gauzy/logo_Gauzy_large.png"], check=True)
        subprocess.run(["rsvg-convert", "-w", "512", "-h", "512", svg_logo, "-o", "/opt/gauzy/logo_Gauzy_512x512.png"], check=True)
        print("[LOGO] Generated PNG logo variants successfully.")
    except Exception as e:
        print(f"[LOGO WARNING] Could not generate PNGs with rsvg-convert: {e}")

# 2. Copy logos into webapp container
print("[LOGO] Copying logos to webapp container...")
subprocess.run(["docker", "exec", "webapp", "mkdir", "-p", "/srv/gauzy/assets/images/logos"], check=True)
subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy.svg", "webapp:/srv/gauzy/assets/images/logos/logo_Gauzy.svg"], check=True)
if os.path.exists("/opt/gauzy/logo_Gauzy.png"):
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy.png", "webapp:/srv/gauzy/assets/images/logos/logo_Gauzy.png"], check=True)
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy_large.png", "webapp:/srv/gauzy/assets/images/logos/logo_Gauzy_large.png"], check=True)
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy_512x512.png", "webapp:/srv/gauzy/assets/images/logos/logo_Gauzy_512x512.png"], check=True)
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy.png", "webapp:/srv/gauzy/assets/images/logos/ever.jpg"], check=True)
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy_large.png", "webapp:/srv/gauzy/assets/images/logos/ever-large.jpg"], check=True)
    subprocess.run(["docker", "cp", "/opt/gauzy/logo_Gauzy_512x512.png", "webapp:/srv/gauzy/assets/images/logos/ever512x512.jpg"], check=True)

# 3. Patch index.html, manifest.json, and inject Octapus Auth Model
print("[HTML/MANIFEST] Updating index.html, manifest.json, and injecting Octapus Auth Model in container...")
if os.path.exists("/opt/gauzy/octapus-auth-model.css"):
    subprocess.run(["docker", "cp", "/opt/gauzy/octapus-auth-model.css", "webapp:/srv/gauzy/assets/octapus-auth-model.css"], check=True)
if os.path.exists("/opt/gauzy/octapus-auth-model.js"):
    subprocess.run(["docker", "cp", "/opt/gauzy/octapus-auth-model.js", "webapp:/srv/gauzy/assets/octapus-auth-model.js"], check=True)

patch_html_cmd = """
sed -i 's|<title>.*</title>|<title>OBMS ERP - Powered by Octapus System</title>|g' /srv/gauzy/index.html
sed -i 's|Gauzy|OBMS ERP|g' /srv/gauzy/index.html
sed -i 's|Ever Co. LTD|Octapus System|g' /srv/gauzy/index.html 2>/dev/null || true
sed -i 's|"name": "Gauzy"|"name": "OBMS ERP"|g' /srv/gauzy/manifest.json
sed -i 's|"short_name": "gauzy"|"short_name": "OBMS ERP"|g' /srv/gauzy/manifest.json
if ! grep -q "octapus-auth-model.css" /srv/gauzy/index.html; then
  sed -i 's|</head>|<link rel="stylesheet" href="assets/octapus-auth-model.css">\\n<script src="assets/octapus-auth-model.js" defer></script>\\n</head>|g' /srv/gauzy/index.html
fi
"""
subprocess.run(["docker", "exec", "webapp", "sh", "-c", patch_html_cmd], check=True)

# 4. Patch i18n JSON translation files
print("[I18N] Processing translation JSON files...")
res = subprocess.run(["docker", "exec", "webapp", "find", "/srv/gauzy/assets/i18n", "-name", "*.json"], capture_output=True, text=True, check=True)
i18n_files = res.stdout.strip().split()

def replace_text(text):
    if not isinstance(text, str):
        return text
    # Replacements in hierarchical order
    text = text.replace("Ever® Gauzy™", "OBMS ERP")
    text = text.replace("Ever Gauzy", "OBMS ERP")
    text = text.replace("Ever®", "OBMS ERP")
    text = text.replace("Gauzy AI", "OBMS ERP AI")
    text = text.replace("Gauzy Platform", "OBMS ERP Platform")
    text = text.replace("Gauzy Desktop", "OBMS ERP Desktop")
    text = text.replace("Gauzy Server", "OBMS ERP Server")
    text = text.replace("Gauzy Timer", "OBMS ERP Timer")
    text = text.replace("Gauzy Agent", "OBMS ERP Agent")
    text = text.replace("Gauzy", "OBMS ERP")
    text = text.replace("gauzy", "OBMS ERP")
    text = text.replace("GAUZY", "OBMS ERP")
    text = text.replace("Ever Co. LTD", "Octapus System")
    text = text.replace("Ever Co. Ltd", "Octapus System")
    text = text.replace("Ever Co.", "Octapus System")
    text = text.replace("Ever Technologies LTD", "Octapus System")
    text = text.replace("Ever Technologies", "Octapus System")
    text = text.replace("Ever Works", "Octapus System")
    text = text.replace("Ever Async", "Octapus System Async")
    text = text.replace("Ever ID", "Octapus ID")
    text = text.replace("All rights reserved.", "All rights reserved. Powered by Octapus System.")
    return text

def walk_and_replace(obj):
    if isinstance(obj, dict):
        return {k: walk_and_replace(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [walk_and_replace(item) for item in obj]
    elif isinstance(obj, str):
        return replace_text(obj)
    return obj

for fpath in i18n_files:
    fname = os.path.basename(fpath)
    tmp_local = f"/tmp/{fname}"
    subprocess.run(["docker", "cp", f"webapp:{fpath}", tmp_local], check=True)
    with open(tmp_local, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = walk_and_replace(data)
    with open(tmp_local, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    subprocess.run(["docker", "cp", tmp_local, f"webapp:{fpath}"], check=True)
    os.remove(tmp_local)
    print(f"[I18N] Rebranded {fname}")

# 5. Patch JS chunks for currency and names
print("[JS] Patching JS bundles for AED currency, branding, and credentials...")
patch_js_cmd = """
cd /srv/gauzy
for f in *.js; do
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
done
"""
subprocess.run(["docker", "exec", "webapp", "sh", "-c", patch_js_cmd], check=True)

# 6. Specific login chunk patch (1404.d530167e5825dfd1.js)
print("[LOGIN] Updating 1404 demo credentials and labels...")
patch_login_cmd = """
sed -i 's|" admin@ever.co"|" admin"|g' /srv/gauzy/1404.d530167e5825dfd1.js 2>/dev/null || true
sed -i 's|" local.admin@ever.co"|" admin"|g' /srv/gauzy/1404.d530167e5825dfd1.js 2>/dev/null || true
sed -i 's|n.SpI("",n.bMT(19,20,"LOGIN_PAGE.DEMO.LABELS.PASSWORD")," admin")|n.SpI("",n.bMT(19,20,"LOGIN_PAGE.DEMO.LABELS.PASSWORD")," admin123")|g' /srv/gauzy/1404.d530167e5825dfd1.js 2>/dev/null || true
sed -i 's|n.SpI("",n.bMT(30,26,"LOGIN_PAGE.DEMO.LABELS.PASSWORD")," admin")|n.SpI("",n.bMT(30,26,"LOGIN_PAGE.DEMO.LABELS.PASSWORD")," admin123")|g' /srv/gauzy/1404.d530167e5825dfd1.js 2>/dev/null || true
"""
subprocess.run(["docker", "exec", "webapp", "sh", "-c", patch_login_cmd], check=True)

print("=== OBMS ERP REBRANDING COMPLETED SUCCESSFULLY ===")
