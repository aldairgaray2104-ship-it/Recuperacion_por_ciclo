import json

with open('real_summary.json', 'r', encoding='utf-8') as f:
    summary = json.load(f)

# Read app.js
with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Prepare exact JS object for REAL_SUMMARY
real_summary_js = f"const REAL_SUMMARY = {json.dumps(summary, indent=4)};"

# Let's inspect real_summary_js
print("REAL SUMMARY JS generated!")
