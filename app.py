import os
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from models import *
from signals import fill_old_values_on_create, update_equipment_from_log, generate_inventory_number
from dotenv import load_dotenv

# ---------- ЗАГРУЗКА ПЕРЕМЕННЫХ ИЗ .env ----------
load_dotenv()

# ---------- ПОДКЛЮЧЕНИЕ К БД ----------
db.connect()

# ---------- FLASK ПРИЛОЖЕНИЕ ----------
app = Flask(__name__)

# Берем SECRET_KEY из .env или используем значение по умолчанию
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing-only')

# Дополнительные настройки из .env
app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'

# ---------- НАСТРОЙКА АДМИНКИ ----------
admin = Admin(app, name='Управление оборудованием', template_mode='bootstrap4')

# Регистрируем все модели (кроме Equipment и EquipmentLog)
admin.add_view(ModelView(EquipmentType))
admin.add_view(ModelView(EquipmentModel))
admin.add_view(ModelView(Location))
admin.add_view(ModelView(Department))
admin.add_view(ModelView(Employee))
admin.add_view(ModelView(Approval))


# ---------- КАСТОМНЫЙ VIEW ДЛЯ ЛОГОВ ----------
class EquipmentLogView(ModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            fill_old_values_on_create(model)
        return super().on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        if is_created:
            update_equipment_from_log(model)
        return super().after_model_change(form, model, is_created)


admin.add_view(EquipmentLogView(EquipmentLog))


# ---------- КАСТОМНЫЙ VIEW ДЛЯ ОБОРУДОВАНИЯ ----------
class EquipmentView(ModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            generate_inventory_number(model)
        return super().on_model_change(form, model, is_created)


admin.add_view(EquipmentView(Equipment))


# ---------- ГЛАВНАЯ СТРАНИЦА ----------
@app.route('/')
def home():
    return '''
    <h1>🏢 Управление оборудованием</h1>
    <p>Перейдите в <a href="/admin">админку</a> для управления</p>
    <hr>
    <p><small>Flask-Admin панель управления</small></p>
    '''


# ---------- ЗАПУСК ----------
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    print("\n" + "=" * 50)
    print("✅ Сервер готов к работе!")
    print("=" * 50)
    print(f"  - Главная:  http://127.0.0.1:{port}")
    print(f"  - Админка:  http://127.0.0.1:{port}/admin")
    print(f"  - Режим DEBUG: {debug}")
    print("=" * 50 + "\n")

    app.run(host=host, port=port, debug=debug)