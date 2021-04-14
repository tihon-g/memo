DEFAULT_CHARSET = 'utf-8'
import os
import dj_database_url

DEBUG = os.getenv("DEBUG", default="False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {'default': dj_database_url.parse(os.getenv("DATABASE_URL", default='sqlite:///memo.sqlite'))}

# db_from_env = dj_database_url.config()
# DATABASES['default'].update(db_from_env)
DATABASES['default']['CONN_MAX_AGE'] = 500
# for tests
#DATABASES['default']['TEST'] = os.path.join(BASE_DIR, 'db_test.sqlite3')

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1 localhost").split(" ")
#print(f'django settings: DEBUG={DEBUG}')

CORS_ORIGIN_ALLOW_ALL = True


CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8000"
]
if os.getenv('SERVER'):
    ALLOWED_HOSTS.append(os.getenv('SERVER'))
    CORS_ORIGIN_WHITELIST = [
        f"https://{os.getenv('SERVER')}",
        'https://127.0.0.1:8000',
    ]
    ALLOWED_HOSTS.append(os.getenv('SERVER'))
else:
    CORS_ORIGIN_WHITELIST = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://localhost:8000',
        'https://127.0.0.1:8000',
    ]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_listfilter_dropdown',
    'corsheaders',
    'social_django',  # https://github.com/omab/python-social-auth/blob/master/MIGRATING_TO_SOCIAL.md#settings
    'sslserver',
    #'storages',
    'channels',
    'chat',
    'webapp',
    'furniture',
    'material',
    'render',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rendering.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  # [os.path.join(BASE_DIR, 'templates')],
            [os.path.join(BASE_DIR, a, 'templates', a) for a in INSTALLED_APPS[-4:]],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # add this
                'social_django.context_processors.login_redirect',  # add this
            ],
            'libraries': {
                'mat_tags': 'material.templatetags.mat_tags',
                'product_tags': 'furniture.templatetags.product_tags',
                'render_tags': 'render.templatetags.render_tags',
            }
        },
    },
]

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

WSGI_APPLICATION = 'rendering.wsgi.application'
#ASGI_APPLICATION = 'rendering.asgi.application'
ASGI_APPLICATION = 'rendering.routing.application'


AUTHENTICATION_BACKENDS = [
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.instagram.InstagramOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html
# Channel layers allow you to talk between different instances of an application. They’re a useful part of making a distributed realtime application if you don’t want to have to shuttle all of your messages or events through a database.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('REDIS_HOST', '127.0.0.1'), int(os.getenv('REDIS_PORT', '6379')))],
        },
    },
}

# Do Not Use In Production
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }


# Internationalization
LANGUAGE_CODE = 'en-us'
# LANGUAGES = [('ru', 'Russian'),('en', 'English'),]
TIME_ZONE = 'UTC' #todo fix

USE_I18N = True
USE_L10N = True
USE_TZ = True

## Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# swatch settings for script which prepared swatches
MATERIAL_SWATCH_DPI = 96
MATERIAL_SWATCH_INCHSIZE = (4, 4)

STATICFILES_DIRS = [os.path.join(BASE_DIR, a, 'static') for a in INSTALLED_APPS[-4:]]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

#emailing
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'grigorenko.tihon@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = 587

#LOGIN_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# SSL/https/redirect/CSRF
#SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
#print(f"SECURE_SSL_REDIRECT = {SECURE_SSL_REDIRECT}")

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

X_ACCEL_REDIRECT_PREFIX = 'media'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Force HTTPS in the final URIs

#SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_link']  # add this
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {        # add this
  'fields': 'id, name, email, picture.type(large), link'
}
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [                 # add this
    ('name', 'name'),
    ('email', 'email'),
    ('picture', 'picture'),
    ('link', 'profile_url'),
]
LOGIN_REDIRECT_URL = "/"
# # add this code
# SOCIAL_AUTH_INSTAGRAM_KEY = YOUR_CLIENT_ID         #Client ID
# SOCIAL_AUTH_INSTAGRAM_SECRET = YOUR_CLIENT_SECRET  #Client SECRET
# SOCIAL_AUTH_INSTAGRAM_EXTRA_DATA = [('user', 'user'),

#PYTHONASYNCIODEBUG = 1

#MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "renders")   #'media/'
MEDIA_ROOT = os.getenv('RENDER_DIR', os.path.join(os.path.dirname(BASE_DIR), "renders"))
MEDIA_URL = f'/media/'

os.environ['DJANGO_BASE_DIR'] = BASE_DIR

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SECURE_SSL_REDIRECT = True
#SECURE_REDIRECT_EXEMPT = [r'^*+$']
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=['127.0.0.1']


#APPEND_SLASH=False