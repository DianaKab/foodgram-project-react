####  IP: http://51.250.26.133/admin/
####  Логин: Dianakab
####   Пароль: 5714

# «Продуктовый помощник»

API проекта сайт Foodgram.
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка проекта

Как установить проект:

```bash
git clone git@github.com:DianaKab/foodgram-project-react.git

cd foodgram-project-react
```
Cоздать и активировать виртуальное окружение:

В Windows:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
В macOS или Linux:
```
python3 -m venv venv
```
```
source venv/bin/activate
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

## Документация проекта

`/redoc/`


## Авторы

- [@DianaKab](https://github.com/DianaKab)
