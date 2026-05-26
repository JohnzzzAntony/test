import django.template.context
from copy import copy

def patched_copy(self):
    # Use object.__new__ to create a new instance of the same class without calling __init__
    duplicate = object.__new__(self.__class__)
    # Copy all dictionary attributes
    duplicate.__dict__.update(self.__dict__)
    # Create a shallow copy of the dicts list
    duplicate.dicts = self.dicts[:]
    # Create a copy of the render_context if it exists
    if hasattr(self, 'render_context'):
        duplicate.render_context = copy(self.render_context)
    return duplicate

# Apply the patches to all context classes in django.template.context
django.template.context.BaseContext.__copy__ = patched_copy
django.template.context.Context.__copy__ = patched_copy
django.template.context.RequestContext.__copy__ = patched_copy
django.template.context.RenderContext.__copy__ = patched_copy

print("Improved Django Context monkeypatch applied (Python 3.14 compatible).")
