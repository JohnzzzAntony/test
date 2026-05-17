import django.template.context
from copy import copy

def patched_base_context_copy(self):
    # Use object.__new__ to create a new instance without calling __init__ or __copy__
    duplicate = object.__new__(self.__class__)
    # Copy all attributes from __dict__ to ensure we don't miss anything (like autoescape in Context)
    duplicate.__dict__.update(self.__dict__)
    # Manually handle dicts as Django does
    duplicate.dicts = self.dicts[:]
    return duplicate

def patched_context_copy(self):
    duplicate = patched_base_context_copy(self)
    duplicate.render_context = copy(self.render_context)
    return duplicate

# Apply the patches
django.template.context.BaseContext.__copy__ = patched_base_context_copy
django.template.context.Context.__copy__ = patched_context_copy

print("Django Context monkeypatch applied.")
