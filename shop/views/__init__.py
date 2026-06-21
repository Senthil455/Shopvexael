# Re-export all views from main module for backward compatibility
# This file enables splitting views.py into logical submodules.
# Each submodule (auth.py, customer.py, seller.py, admin.py, api.py)
# can be populated incrementally without breaking imports.
from .main import *
