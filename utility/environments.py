import os

PRODUCTION = 'production'
TESTING = 'testing'
DEVELOPMENT = 'development'


def set_settings_module():
    if os.environ.get('ENVIRONMENT') == PRODUCTION:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxScout.settings.production')
    elif os.environ.get('ENVIRONMENT') == TESTING:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxScout.settings.testing')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxScout.settings.development')
