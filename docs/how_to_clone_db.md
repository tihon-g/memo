1. сливаешь базу с прода в виде json
ssh root@165.232.53.1
source /home/django/envs/memo/bin/activate
cd /home/django/rendering/
python manage.py dumpdata furniture material render > dump.json
выкачиваешь json себе

2. копируешь из гита приложение (если нету), например
git remote add github https://github.com/tihon-g/rendering.git
git pull github

3. там нет файла настроек ( можно взять из репо croc gitlab )


4. устанавливаешь в своем приложении использование локальной базы sqlite ( в settings )

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'memo.sqlite'),
    }
}
```

5. создаешь базу запустив миграцию
`python manage.py migrate`

6. создаешь супер-юзера себя
python manage.py createsuperuser

7. наливаешь данные в базу
`python manage.py loaddata dump.json`

