# FastAPI Library Project📖

Данная программа предназначена для формирования собственной библиотеки.

---
## Функционал проекта:

- Обновление, добавление и удаление книг в бибилиотеке
- Возможность получить полную информацию о библиотеке и книгах в ней
- Возможность отметить книгу как прочитанную 

---
## Используемые библиотеки:
```commandline
fastapi
sqlalchemy
sqlalchemy.orm
pydantic
fastapi.templating
fastapi.responses
```

---
## Запуск проекта:
1. Установить зависимости
```commandline
pip install fastapi
pip install sqlalchemy
pip install pydantic
pip install jinja2 
```
При необходимости установить дополнительные библиотеки, которые запрашивает программа.
2. Подставить свои данные в следующую  строчку файла `main.py`:
```python
engine = create_engine("your_data")
```
3. Запустить программу через консоль с помощью команды:
```commandline
uvicorn main:app --reload
```


