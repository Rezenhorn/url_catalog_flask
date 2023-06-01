# Приложение для каталогизации веб-ресурсов
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/release/python-379/) [![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/2.2.x/) [![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/) [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## Описание:
Приложение разработано с помощью фреймворка flask, работает с базой данных SQLite, имеет API и веб-интерфейс.
Цель приложения: каталогизация и структурирование информации по различным веб-ресурсам.
Приложение может обработать полученные ссылки в формате URL, раскладывает ее на протокол, домен, доменную зону, путь и параметры.
Ссылки могут быть переданы через API в формате строки или файла csv. Также имеется возможность загрузки данных через веб-страницу с формой. Список разложенных по частям URL из базы данных можно получить через API или на веб-странице. Также предусмотрено логирование запросов и ответов и вывод логов.
Работа с API и веб-страницей доступна только зарегистрированным пользователям.

## Технологии:
- Python 3.7.9
- Flask 2.2
- SQLAlchemy
- Bootstrap5
- Docker

## Запуск проекта локально:

### Клонировать репозиторий и перейти в него:
```bash
git clone https://github.com/Rezenhorn/test_task_flask.git
```
### Убедиться, что на компьютере установлен и запущен Docker.
### Собрать и запустить контейнер из корневой папки приложения:

```bash
docker build -t application:latest .
```

```bash
docker run --name application -d -p 8000:5000 --rm application:latest
```

Проект станет доступен по адресу <http://localhost:8000/>

Возможно возникновение ошибки при запуске контейнера: сбиваются окончания строк (EOL) у файла `boot.sh`. Необходимо в текстовом редакторе (например, Notepad++) изменить формат EOL: Edit > EOL Conversion > Unix/OSX Format.

### Остановка контейнера

Необходимо найти работающий контейнер и его CONTAINER ID:

```bash
docker container ls
```

И остановить контейнер командой:

```bash
docker stop <CONTAINER ID>
```

## Эндпоинты API:
### Регистрация пользователя
**POST запрос:**
```
http://localhost:8000/api/create_user
```
Для регистрации пользователя необходимо в теле запроса в формате JSON передать юзернейм, пароль и email:

```json
{
  "username": "username",
  "password": "1234567890",
  "email": "1@1.ru"
}
```

В случае успеха, пользователь будет зарегистрирован.

### Получение токена пользователя и его дальнейшее использование

Для получения токена для работы с другими эндпоинтами, необходимо с указанием учетных данных (username, password) отправить запрос на:

**POST запрос:**

```
http://localhost:8000/api/tokens
```
Учетные данные в сервисе Postman необходимо указывать во вкладке Authorization, тип - Basic Auth.
Сервис вернет токен аутентификации:

```json
{
  "token": "hAnYID3nUsVpb12ll20fH72j33xdwXFa"
}
```

В дальнейшем, данный токен необходимо передавать вместе с запросом (Bearer Token), чтобы получить доступ к остальным эндпоинтам.

### Получение ссылкок из БД
**GET запрос:**

```
http://localhost:8000/api/link
```

Сервис возвращает список всех разложенных URL из БД в формате JSON. Пример ответа:

```json
[{
  "domain": "someshop.ru",
  "domain_zone": "ru",
  "id": 7,
  "parameters": {
    "page": "1",
    "perpage": "20"
   },
   "path": "/catalog/iphone",
   "protocol": "https",
   "uuid": "97764797-1096-44af-809a-ad500e9c794b"
}]
```

Также предусмотрена выборка по id, uuid и domain_zone. В таком случае, эндпоинт может выглятеть так:

```
http://localhost:8000/api/link?id=2
```

### Загрузка ссылки в БД
**POST запрос:**

```
http://localhost:8000/api/link
```

В теле запроса должна передаваться ссылка в формате JSON. Ключ: 'url'. Например:

```json
{
  "url": "https://someshop.ru/catalog/iphone?page=1&perpage=20"
}
```

В случае успешного запроса, сервис добавляет URL в ДБ и возвращает разложенную ссылку URL в формате JSON:

```json
{
  "domain": "someshop.ru",
  "domain_zone": "ru",
  "id": 1,
  "parameters": {
    "page":"1",
    "perpage":"20"
  },
  "path": "/catalog/iphone",
  "protocol": "https",
  "uuid": "14dd3728-4519-4c34-bdf6-ee4ef7b37bcd"
}
```

### Загрузка ссылок из csv-файла
**POST запрос:**

```
http://localhost:8000/api/load_csv
```

Запрос должен содержать в себе csv файл с перечнем ссылок (формат файла - каждая новая строка одна ссылка).
В случае успешного запроса, сервис добавляет новые URL из файла в БД, возвращает список разложенных URL, добавленных в базу, а также общий статус обработки файла (количество обрабатываемых ссылок, количество ошибок, количество ссылок, направленных на сохранение в БД).
Для примера, можете использовать заготовленный файл example.csv в папке app.

Пример ответа:

```json
[{
  "errors": 1,
  "links_to_process": 2,
  "success_additions": 1
},
{
  "domain": "blog.miguelgrinberg.com",
  "domain_zone": "com",
  "id": 1,
  "parameters": {},
  "path": "/post/handling-file-uploads-with-flask",
  "protocol": "https",
  "uuid": "10ac87d5-79c1-4649-a728-b94c5906924a"
}]
```

### Получение последних логов
**GET запрос:**

```
http://localhost:8000/api/get_log
```

Возвращает последние 20 строчек лога.