import re
import os
import glob
import subprocess

print("=== INSPECTING WEBAPP ASSETS FOR REBRANDING ===")
# Inspect webapp container files
res = subprocess.run(["docker", "exec", "webapp", "find", "/srv/gauzy", "-name", "*.json"], capture_output=True, text=True)
json_files = res.stdout.strip().split()
print(f"Found {len(json_files)} json files in webapp")

res_js = subprocess.run(["docker", "exec", "webapp", "find", "/srv/gauzy", "-maxdepth", "1", "-name", "*.js"], capture_output=True, text=True)
js_files = res_js.stdout.strip().split()
print(f"Found {len(js_files)} js files in webapp")

