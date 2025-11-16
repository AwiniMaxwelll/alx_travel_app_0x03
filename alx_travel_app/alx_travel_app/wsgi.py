"""
WSGI config for alx_travel_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os, sys


# the project path
# path = '/home/lordlinker/alx_travel_app'
# if path not in sys.path:
#     sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'alx_travel_app.settings'

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

application = get_wsgi_application()
