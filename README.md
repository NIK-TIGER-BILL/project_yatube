![logo](https://user-images.githubusercontent.com/59732804/112229268-b60dfe80-8c43-11eb-9bc9-a05a5e6ddbf0.png)
# Yatube :tada:  
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?style=flat-square&logo=SQLite)](https://www.sqlite.org/)
[![pytest](https://img.shields.io/badge/-pytest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)

Социальная сеть в которой реализована возможность для публикации личных дневников. Это сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи могут заходить на чужие страницы, подписываться на других авторов и комментировать их записи. Автор может выбрать имя и уникальный адрес для своей страницы. Записи можно отправить в группу и посмотреть в ней записи разных авторов.

## Для запуска проекта
Нужно:  
- Создайте виртуальное окружение и подключите его.
```
python -m venv venv
source venv/Scripts/activate
```
- Установите все зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Запустите проект
```
python manage.py runserver
```
Если вы это сделали на локальной машине. Сайт будет доступен по адресу http://localhost/ / http://127.0.0.1:8000/
