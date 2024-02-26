логин, пароль и почта администратора:
flyshy 
12345 
sd@cds.com
Домен
```
https://foodgramme.bounceme.net/
```

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

Создаем файл .env в директории /infra и заполняем поля нужными значениями:

```
POSTGRES_DB=foodgrasm
POSTGRES_USER=flyshy
POSTGRES_PASSWORD=12345
DB_NAME=foodgrasm

DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=foodgramme.bounceme.net,158.160.0.95,127.0.0.1,localhost
DEBUG=False
```

Запускаем Docker Compose с конфигурацией из файла docker-compose.production.yml:

```
docker compose -f docker-compose.production.yml up -d
```

Собираем статику:

```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input  
```

Выполняем миграции:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Создаем админа:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Переходим по ссылке, авторизуемся:

```
http://localhost:8080/admin/
```

Добавляем необходимые теги:
```
http://localhost:8080/admin/recipes/tag/add/
```

Импортируем ингридиенты в формате json:
```
http://localhost:8080/admin/recipes/ingredient/import/
```

### Примеры запросов данных к API:

Регистрация пользователя:

_Запрос_
POST
```
http://localhost:8080/api/users/
```
_Ответ_
```
{
  "email": "iamproyes@admin.ru",
  "username": "avenge.me",
  "first_name": "Никита",
  "last_name": "Петров",
  "password": "supersecretpass12345"
}
```

Получение списка тегов:

_Запрос_
GET
```
http://localhost:8080/api/tags/
```

_Ответ_
```
[
  {
   "id": 0,
    "name": "Завтрак",
    "color": "#E26C2D",
    "slug": "breakfast"
  }
]
```

Создание рецепта:
_Доступно только авторизованному пользователю_

_Запрос_
POST
```
http://localhost:8080/api/recipes/
```

_Ответ_
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Добавить рецепт в избранное
_Доступно только авторизованному пользователю_

_Запрос_
POST
```
http://localhost:8080/api/recipes/{id}/favorite/
```

_Ответ_
```
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```

Скачать список покупок
_Скачать файл со списком покупок в формате TXT. Доступно только авторизованным пользователям._

_Запрос_
GET
```
http://localhost:8080/api/recipes/download_shopping_cart/
```

Подробная документация с описанием всех запросов и ответов доступная по ссылке:

```
http://localhost:8080/api/docs/
```

### Контактная информация
Для связи с мной в GitHub можно перейти по ссылке:

```
https://github.com/F1yShy
```
Также вы можете написать на электронную почту, указанную в профилях на GitHub. Буду рад ответить на ваши вопросы и обсудить возможные совместные проекты
