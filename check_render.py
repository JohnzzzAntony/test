import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from django.template.loader import render_to_string
html = render_to_string('index.html')

import re
matches = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
for img in matches[:20]:
    print(img)


