"""
API Routes Module
================

Import all route modules for easy access.
"""

# Import all route modules
from . import chat
from . import documents  
from . import health
from . import ai
from . import service_guide

# Make routers easily accessible
__all__ = ['chat', 'documents', 'health', 'ai', 'service_guide']
