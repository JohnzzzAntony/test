import os

def clean_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        if b'\x00' in content:
            print(f"Cleaning {filepath}...")
            # Try to decode as UTF-16 if it looks like it, otherwise just strip nulls
            try:
                # If it's mostly nulls, it might be UTF-16
                text = content.decode('utf-16')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
            except:
                # Just strip nulls and hope for the best
                clean_content = content.replace(b'\x00', b'')
                with open(filepath, 'wb') as f:
                    f.write(clean_content)
            return True
    except Exception as e:
        print(f"Could not process {filepath}: {e}")
    return False

def main():
    exclude_dirs = {'.git', '.venv', '__pycache__', 'node_modules', 'staticfiles', 'media'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.env', '.md')):
                clean_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
