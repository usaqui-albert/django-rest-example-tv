from TapVet.settings import *  # NOQA


DEBUG = False

ALLOWED_HOSTS = [
    '.blanclabs.com',
    'localhost',
    '.tapvet.com'
]
ADMINS = [
    ('TapVet Team', 'yourteam@tapvet.com'),
]

REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': True  # Default: False
}

# HTTPS SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
