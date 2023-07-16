# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

### Описание:

# Социальная сеть yatube.

Проект yatube является социакльной сетью для публикации личных дневников. Пользователь может создать свою персональную страницу. На которой можно посмотреть все созданные им записи. Пользователи могут заходить на чужие страницы, подписываться на других авторов и комментировать их записи. Каждую созданную запись можно отнести к имеющимся на сайте сообществам, пользователь может посмотреть все записи сообщества.

### Технологии

Python 3.7

Django 3.2


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Sarugot/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
