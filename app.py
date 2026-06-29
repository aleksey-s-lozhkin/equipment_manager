from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from models import *
from signals import fill_old_values_on_create, update_equipment_from_log
from dotenv import load_dotenv
import os

# ---------- ЗАГРУЗКА .env ----------
load_dotenv()

# ---------- ПОДКЛЮЧЕНИЕ К БД ----------
db.connect()

# ---------- FLASK ПРИЛОЖЕНИЕ ----------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing-only')
app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'

# ---------- ВОТ ЭТО ГЛАВНОЕ! СМЕНА ТЕМЫ ----------
app.config['FLASK_ADMIN_SWATCH'] = 'simplex'

# ---------- НАСТРОЙКА АДМИНКИ ----------
admin = Admin(
    app,
    name='Управление оборудованием',
    template_mode='bootstrap4'
)

# Регистрируем модели (кроме Equipment и EquipmentLog)
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


admin.add_view(ModelView(Equipment))


# ---------- ГЛАВНАЯ СТРАНИЦА ----------
@app.route('/')
def home():
    return '''
    <h1>🏢 Управление оборудованием</h1>
    <p>Перейдите в <a href="/admin">админку</a> для управления</p>
    '''


# ---------- ЗАПУСК ----------
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    print("\n" + "=" * 60)
    print("✅ СЕРВЕР ЗАПУЩЕН!")
    print("=" * 60)
    print(f"  📌 Главная:    http://127.0.0.1:{port}")
    print(f"  📌 Админка:    http://127.0.0.1:{port}/admin")
    print(f"  🔧 Режим DEBUG: {debug}")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug)