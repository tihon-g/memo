DEFAULT_CHARSET = 'utf-8'
import os
import dj_database_url

# load_dotenv does not override existing System environment variables.
# To override, pass override=True to load_dotenv().

DEBUG = os.getenv("DEBUG", default="False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {'default': dj_database_url.parse(os.getenv("DATABASE_URL", default='sqlite:///memo.sqlite'))}
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1 localhost").split(" ")
print(f'django settings: DEBUG={DEBUG}')

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]
if os.getenv('SERVER'):
    CORS_ORIGIN_WHITELIST.append(f"https://{os.getenv('SERVER')}")
    ALLOWED_HOSTS.append(os.getenv('SERVER'))

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
    #'sslserver',
    #'storages',
    #'channels',
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
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
CSRF_USE_SESSIONS = os.getenv('CSRF_USE_SESSIONS', 'False') == 'True'
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

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "renders")   #'media/'
MEDIA_URL = f'/media/'

os.environ['DJANGO_BASE_DIR'] = BASE_DIR
