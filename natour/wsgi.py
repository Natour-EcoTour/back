"""
WSGI config for natour project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'natour.settings')

import otel_config  # Do this after sys.path and os.environ

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

