import os

env_path = '.env'
with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    # Remove null bytes and strip whitespace
    clean_line = line.replace('\x00', '').strip()
    if clean_line:
        clean_lines.append(clean_line)

# Add a newline between blocks for readability
final_content = "\n".join(clean_lines) + "\n"

with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(final_content)

print("Cleaned .env file.")
