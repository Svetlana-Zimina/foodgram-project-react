## Описание
«Фудграм» — сайт, на котором зарегистрированные пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и 
подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать 
список продуктов, которые нужно купить для приготовления выбранных блюд. Незарегистрированным пользователям доступен просмотр
списка рецептов или отдельного рецепта.


## Технологии
- Python 3.7
- Django 3.2.3
- Djangorestframework 3.14.0
- Djoser 2.2.0 
- Gunicorn 20.1.0
- Docker

К проекту подключена база PostgreSQL. Для тестирования подключена база SQLite.
Предусмотрена автоматическая упаковка частей проекта(backend, frontend, gateway, db) в образы с помощью Docker и размещение их 
в удаленном репозитории на DockerHub, а также автоматизация деплоя на удаленный сервер с помощью GitHub actions.
На удаленном сервере установлена операционная система Ubuntu.
Доступна документация API.


## Локальный запуск проекта

1. ### Склонируйте репозиторий:
```
git clone git@github.com:Svetlana-Zimina/foodgram-project-react.git
```

2. ### Создайте и активируйте виртуальное окружение:
Команда для установки виртуального окружения на Mac или Linux:
```
python3 -m venv env
source env/bin/activate
```

Команда для установки виртуального окружения на Windows:
```
python -m venv venv
source venv/Scripts/activate
```

3. ### В корневой дирректории создайте файл .env по образцу .env.example.

4. ### Установите зависимости:
```
cd backend
pip install -r requirements.txt
```

5. ### Проведите миграции:
```
python manage.py migrate
```

6. ### Наполните тестовую базу ингредиентами:
```
python manage.py import_ingredients
```

7. ### При необходимости создайте суперпользователя:
```
python manage.py createsuperuser
```

8. ### Запустите локальный сервер:
```
python manage.py runserver
```


## Локальный запуск проекта через Docker

1. ### Установите docker согласно [инструкции](https://docs.docker.com/engine/install/ubuntu/)
Пользователям Windows нужно будет подготовить систему, установить для неё ядро Linux — и после этого установить Docker.

2. ### В корневой дирректории выполните команды:
```
docker-compose up
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py import_ingredients
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic
```


## Просмотр API документации

1. ### Перейдите в папку infra:
```
cd infra/
```

2. ### Выполните команду:
```
docker-compose up
```

Документация будет доступна по адресу: http://localhost/api/docs/


## Установка проекта на удалённом сервере

> [!IMPORTANT] 
> При выпуске проекта в продакшн необходимо, чтобы DEBUG = False и переменная DATABASE_ENV=prod (чтобы подключилась база Postgre)

1. ### Выполните вход на удаленный сервер

2. ### Установите Docker Compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

3. ### Создайте папку foodgram:
```
sudo mkdir foodgram
```

4. ### В папке foodgram создайте файл docker-compose.production.yml и скопируйте туда содержимое файла docker-compose.production.yml из проекта:
```
cd foodgram
sudo touch docker-compose.production.yml 
sudo nano docker-compose.production.yml
```

5. ### В файл настроек nginx добавить домен сайта:
```
sudo nano /etc/nginx/sites-enabled/default
```

6. ### После корректировки файла nginx выполнить команды:
```
sudo nginx -t
sudo service nginx reload
```

7. ### Из дирректории foodgram выполнить команды:
```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
sudo docker system prune -a
```

Если необходимо создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```


## Автоматический деплой проекта на сервер.

Предусмотрен автоматический деплой проекта на сервер с помощью GitHub actions. Для этого описан workflow файл:
.github/workflows/main.yml
После деплоя в проекте предусмотрена отправка смс в телеграм чат. Код чат-бота находится в репозитории [homework_bot](https://github.com/Svetlana-Zimina/homework_bot)

1. ### После внесения правок в проект выполните команды:
```
git add .
git commit -m 'комментарий'
git push
```

GitHub actions выполнит необходимые команды из workflow файла - контейнеры на удаленном сервере перезапустятся.

2. ### Добавьте ингредиенты в базу:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
```

3. ### Для правильной работы workflow необходимо добавить в Secrets данного репозитория на GitHub переменные окружения:
```
DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>
HOST=<ip сервера>
POSTGRES_DB=<название базы данных>
POSTGRES_PASSWORD=<пароль к базе данных>
POSTGRES_USER=<пользователь базы данных>
SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>
SSH_PASSPHRASE=<пароль для сервера, если есть>
USER=<username для подключения к удаленному серверу>
TELEGRAM_TO=<id вашего Телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```


## Документация API после деплоя на удаленный сервер доступна по адресу:
ДоменВашегоСайта/api/docs/


## Авторы
Светлана Зимина
https://github.com/Svetlana-Zimina