import re

html = open('homepage.html', 'rb').read().decode('utf-8', errors='ignore')
for img in re.findall(r'<img[^>]+src=[\"\']([^\"\']+)[\"\'][^>]*>', html)[:30]:
    print(img)
