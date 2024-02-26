логин, пароль и почта администратора:
flyshy 
12345 
sd@cds.com

### Проект Foodgram

Проект Foodgram предназначен для того, чтобы размещать собственные рецепты пользователей, которые очень любят готовить. Сервис Foodgram предоставляет данную возможность, позволяя поделиться своим рецептом, либо же посмотреть на другие рецепты.

Проект Foodgram доступен по ссылке:

```
https://foodgramme.bounceme.net/
```

### Используемые технологии

Django - фреймворк для создания веб-приложений на языке Python. Он предоставляет множество инструментов для работы с базами данных, шаблонами, формами и многое другое.

Django Rest Framework - расширение для Django, которое позволяет быстро и удобно создавать RESTful API. Оно предоставляет множество инструментов для сериализации и десериализации данных, авторизации и аутентификации пользователей, обработки ошибок и многое другое.

Pytest - фреймворк для автоматического тестирования на языке Python. Он предоставляет множество инструментов для написания и запуска тестов, а также для генерации отчетов о результатах тестирования.

Nginx - http-сервер и обратный прокси-сервер, почтовый прокис-сервер, а также TCP/UDP прокси-сервер общего назначения, позволяющий обслуживать статические запросы, индексные файлы, автоматически создавать списки файлов и многое другое.

Gunicorn — это HTTP-сервер интерфейса шлюза веб-сервера Python.

React — JavaScript-библиотека с открытым исходным кодом для разработки пользовательских интерфейсов.

Docker - это открытая платформа для разработки, доставки и эксплуатации приложений, разработана для более быстрого выкладывания приложений. С помощью docker можно отделить приложение от инфраструктуры и обращаться с инфраструктурой как управляемым приложением.

### Как развернуть проект

Клонируем репозиторий:

```
git clone https://github.com/F1yShy/foodgram-project-react.git
```

Переходим в директорию infra/:

```
cd infra/
```

Создаем файл .env в корневой директории и заполняем поля нужными значениями:

```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

Запускаем Docker Compose с конфигурацией из файла docker-compose.production.yml:

```
docker compose -f docker-compose.production.yml up -d
```

Собираем статику:

```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

Выполняем миграции:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Готово! Сайт доступен по ссылке:

```
http://localhost:8080/
```

### Контактная информация
Для связи с мной в GitHub можно перейти по ссылке:

```
https://github.com/F1yShy
```
Также вы можете написать на электронную почту, указанную в профилях на GitHub. Буду рад ответить на ваши вопросы и обсудить возможные совместные проекты
