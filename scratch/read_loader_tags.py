import inspect
import django.template.loader_tags as lt

source_file = inspect.getsourcefile(lt)
print("Source file:", source_file)

with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = max(0, 190)
end = min(len(lines), 230)
for i in range(start, end):
    print(f"{i+1}: {lines[i]}", end="")
