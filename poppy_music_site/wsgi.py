import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poppy_music_site.settings')

application = get_wsgi_application()
