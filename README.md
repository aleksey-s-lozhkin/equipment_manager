# 🏢 Управление оборудованием
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
## Веб-приложение для учёта средств вычислительной техники (СВТ) с админ-панелью на Flask + Peewee.

## 📋 Возможности
- **Управление оборудованием** — добавление, редактирование, удаление СВТ
- **Каталог моделей** — хранение характеристик оборудования
- **Иерархия мест** — гибкая структура размещения (здание → этаж → помещение)
- **Структура подразделений** — иерархия отделов компании
- **Учёт сотрудников** — закрепление оборудования за пользователями
- **Журнал операций** — автоматическое логирование всех перемещений и изменений
- **Согласования** — система подтверждения операций
- **Дашборд** — главная страница админки со статистикой и быстрым доступом
- **Полная русификация** — интерфейс, меню и названия полей на русском языке
- **Гибкие характеристики** — JSON-поля для дополнительных параметров

## 🚀 Быстрый старт
### Требования
- Python 3.8+
- pip

### Установка
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/yourusername/equipment_manager.git
cd equipment_manager

# 2. Создайте и активируйте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте файл с настройками из шаблона
cp .env.example .env

# 5. Отредактируйте .env (укажите свой SECRET_KEY)
# Можно использовать команду: python -c "import secrets; print(secrets.token_hex(32))"
nano .env

# 6. Примените миграции
python manage.py migrate

# 7. Запустите приложение
python app.py
```
Приложение будет доступно по адресу:

Главная: http://127.0.0.1:8000

Админка: http://127.0.0.1:8000/admin

## 🗂️ Структура проекта
```text
equipment_manager/
├── app.py                 # Главное приложение Flask
├── models.py              # Модели базы данных (Peewee ORM)
├── signals.py             # Логика автоматического заполнения
├── manage.py              # Утилита для управления миграциями
├── requirements.txt       # Зависимости проекта
├── .env                   # Переменные окружения (не в Git!)
├── .env.example           # Шаблон переменных окружения
├── .gitignore             # Игнорируемые файлы
├── migrations/            # Миграции базы данных
│   └── 001_initial.py
├── templates/             # Шаблоны Flask
│   └── admin/
│       └── index.html     # Кастомная главная страница админки
└── README.md
```
## 📊 Модели данных
| Модель	            |Описание|
|--------------------|--------|
| **EquipmentType**	 |Тип оборудования (ноутбук, системный блок, монитор и т.д.)|
| **EquipmentModel**    |Модель с характеристиками (бренд, процессор, ОЗУ и т.д.)|
| **Location**	         |Иерархия мест установки|
| **Department**	        |Иерархия подразделений|
| **Employee**	          |Сотрудники|
| **Equipment**	         |Единицы оборудования (СВТ)|
| **EquipmentLog**	      |Журнал операций|
| **Approval**	          |Согласования операций|
## 🛠️ Управление миграциями
```bash
# Создать новую миграцию
python manage.py create add_new_field

# Применить все миграции
python manage.py migrate

# Откатить последнюю миграцию
python manage.py rollback

# Показать список миграций
python manage.py list
```
## ⚙️ Переменные окружения
Создайте файл .env на основе .env.example:

```env
# Секретный ключ Flask (обязательно измените!)
SECRET_KEY=your-super-secret-key-here

# Настройки базы данных
DATABASE_URL=sqlite:///equipment.db

# Режим отладки
DEBUG=True

# Хост и порт
HOST=0.0.0.0
PORT=8000
```
## 🎨 Тема оформления
По умолчанию используется тема Bootstrap Simplex. Чтобы сменить тему, измените в app.py:

```python
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'  # или 'cosmo', 'darkly', 'slate'
```
Доступные темы: flatly, cosmo, simplex, journal, slate, darkly, lumen, cyborg, united

## 🐛 Устранение проблем
### Порт занят
Если порт 8000 занят, измените PORT в .env:

```env
PORT=8001
```
### Ошибка миграций
Если возникли проблемы с миграциями, удалите базу данных и примените заново:

```bash
rm equipment.db
python manage.py migrate
```
### Ошибка 403 в админке
Убедитесь, что SECRET_KEY установлен в .env до создания админки в app.py.

## 📝 Разработка
### Добавление новой модели
1. Добавьте модель в models.py

2. Создайте миграцию:

```bash
python manage.py create add_new_model
```
3. Отредактируйте файл миграции

4. Примените:

```bash
python manage.py migrate
```
### Настройка админки
Добавьте новый View в app.py:

```python
class NewModelView(ModelView):
    column_labels = {
        'field1': 'Поле 1',
        'field2': 'Поле 2',
    }

admin.add_view(NewModelView(NewModel, name='Название в меню'))
```
## 📄 Лицензия
MIT License

## 👨‍💻 Автор
Aleksey Lozhlkin (@Alserloz)
aleksey.s.lozhkin@gmail.com

## 📞 Поддержка
Если у вас возникли вопросы или проблемы, создайте Issue в репозитории.

## 📌 Changelog
### v1.1.0 (2026-06-29)
✨ Добавлен дашборд на главной странице админки со статистикой

- 🌐 Полная русификация интерфейса (меню, поля, кнопки)

- 🗑️ Удалены GPS-поля из модели Location

- 📝 Поле purchase_date переименовано в delivery_date

- 🔧 Инвентарный номер теперь вводится вручную (без автогенерации)

- 🎨 Изменена тема оформления на Simplex

- 🖱️ Карточки на главной странице стали кликабельными

### v1.0.0 (2026-06-15)
- Первый релиз

- Базовая функциональность учёта оборудования

- Админ-панель Flask-Admin

- Автоматическое логирование операций

- Автогенерация инвентарных номеров


