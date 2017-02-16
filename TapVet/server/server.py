from TapVet.settings import *  # NOQA


DEBUG = False

ALLOWED_HOSTS = [
    '.blanclabs.com'
]
ADMINS = [
    ('Mayra Canas', 'mayrac@blanclabs.com'),
    ('TapVet Team', 'yourteam@tapvet.com'),
]

REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': True  # Default: False
}
