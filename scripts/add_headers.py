import os

HEADER_TEMPLATE_PY = '''"""
* Nom de l'application : RentPilot
* Description : {description}
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
'''

HEADER_TEMPLATE_HTML = '''<!--
* Nom de l'application : RentPilot
* Description : {description}
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
-->
'''

HEADER_TEMPLATE_JS_CSS = '''/*
* Nom de l'application : RentPilot
* Description : {description}
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
*/
'''

def get_description(filename):
    name = os.path.basename(filename)
    if name == 'main.py': return "Application entry point."
    if name == 'settings.py': return "Configuration settings."
    if name.endswith('_routes.py'): return f"Routes for {name.split('_')[0]} module."
    if name.endswith('_service.py'): return f"Service logic for {name.split('_')[0]} module."
    if name.endswith('.html'): return f"Template for {name.split('.')[0]} page."
    if name.endswith('.js'): return f"JavaScript logic for {name.split('.')[0]}."
    if name.endswith('.css'): return f"Styles for {name.split('.')[0]}."
    return f"Source file: {name}"

def apply_header(filepath):
    ext = os.path.splitext(filepath)[1]

    if ext == '.py':
        template = HEADER_TEMPLATE_PY
    elif ext == '.html':
        template = HEADER_TEMPLATE_HTML
    elif ext in ['.js', '.css']:
        template = HEADER_TEMPLATE_JS_CSS
    else:
        return # Skip unknown types

    description = get_description(filepath)
    header = template.format(description=description)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple check if header exists (partial match)
    if "* Auditer par : La CyberConfiance" in content:
        # print(f"Header already exists in {filepath}")
        return

    # For Python files with Shebang or encoding declaration, insert after those
    lines = content.splitlines()
    insert_idx = 0
    if lines and (lines[0].startswith('#!') or lines[0].startswith('# -*')):
        insert_idx += 1
        if len(lines) > 1 and (lines[1].startswith('#!') or lines[1].startswith('# -*')):
            insert_idx += 1

    # Reconstruct content
    new_content = '\n'.join(lines[:insert_idx]) + '\n' + header + '\n'.join(lines[insert_idx:])

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Applied header to {filepath}")

EXCLUDE_DIRS = ['.git', '__pycache__', 'env', 'venv', 'screenshots']

for root, dirs, files in os.walk('.'):
    # Filter out excluded directories
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for file in files:
        if file.endswith(('.py', '.html', '.js', '.css')):
            apply_header(os.path.join(root, file))
