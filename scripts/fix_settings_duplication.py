import os

filepath = 'jkr/settings.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The duplication starts at the first occurrence of "STATIC_URL = \"/static/\"" after line 400
# or similar patterns.
# Let's find the first occurrence of "# =============================================================================" after LOGGING.

logging_end_idx = -1
for i, line in enumerate(lines):
    if '"loggers": {' in line:
        # Found logging, now find its end
        for j in range(i, len(lines)):
            if '}' in lines[j] and (j+1 < len(lines) and '}' in lines[j+1]): # Rough end of LOGGING
                logging_end_idx = j + 2
                break
        if logging_end_idx != -1:
            break

print(f"Logging ends around line {logging_end_idx}")

# The original file should have had SUPABASE settings after logging.
# Let's look for SUPABASE_URL.
supabase_idx = -1
for i in range(logging_end_idx, len(lines)):
    if 'SUPABASE_URL =' in lines[i]:
        supabase_idx = i
        break

if supabase_idx != -1:
    # Everything after the FIRST occurrence of Kimi settings should be kept, 
    # but we need to remove the middle duplication.
    # Actually, it's easier to just truncate the file at the first point of duplication.
    
    # Let's find the second occurrence of "STATIC_URL"
    static_url_occurrences = [i for i, line in enumerate(lines) if 'STATIC_URL = "/static/"' in line]
    if len(static_url_occurrences) > 1:
        truncate_idx = static_url_occurrences[1] - 1 # One line before the second STATIC_URL
        # Wait, the duplication included everything from STATIC_URL onwards.
        # But my last replace_file_content ALSO added Kimi settings at the VERY end.
        
        new_lines = lines[:truncate_idx]
        
        # Add the Kimi settings at the end
        new_lines.append("\n")
        new_lines.append("# =============================================================================\n")
        new_lines.append("# AI SERVICES (KIMI)\n")
        new_lines.append("# =============================================================================\n")
        new_lines.append("NVIDIA_KIMI_API_KEY = env(\"NVIDIA_KIMI_API_KEY\", default=None)\n")
        new_lines.append("KIMI_MODEL = env(\"KIMI_MODEL\", default=\"moonshotai/kimi-k2.6\")\n")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Truncated file at line {truncate_idx} and added Kimi settings.")
    else:
        print("Could not find duplication point.")
else:
    print("Could not find Supabase settings.")
