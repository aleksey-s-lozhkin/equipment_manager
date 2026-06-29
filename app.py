from flask import Flask
from flask_babel import Babel
from flask_admin import Admin, AdminIndexView
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
# Устанавливаем язык по умолчанию (русский)
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'

# Создаём экземпляр Babel
babel = Babel(app)

# ---------- СМЕНА ТЕМЫ ----------
app.config['FLASK_ADMIN_SWATCH'] = 'simplex'


# ---------- КАСТОМНАЯ ГЛАВНАЯ СТРАНИЦА АДМИНКИ ----------
class MyAdminIndexView(AdminIndexView):
    """Кастомная главная страница админки"""

    def render(self, template, **kwargs):
        # Добавляем статистику для отображения на главной
        stats = {
            'equipment_types': EquipmentType.select().count(),
            'equipment_models': EquipmentModel.select().count(),
            'locations': Location.select().count(),
            'departments': Department.select().count(),
            'employees': Employee.select().count(),
            'equipment': Equipment.select().count(),
            'logs': EquipmentLog.select().count(),
        }
        return super().render(
            template,
            stats=stats,
            **kwargs
        )

    # Переопределяем шаблон для использования container-fluid
    def get_base_template(self):
        return 'admin/master.html'

# ---------- НАСТРОЙКА АДМИНКИ ----------
admin = Admin(
    app,
    name='Управление оборудованием',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView()
)

# ---------- КАСТОМНЫЕ VIEW ДЛЯ РУССКИХ НАЗВАНИЙ ----------

class EquipmentTypeView(ModelView):
    column_labels = {
        'id': 'ID',
        'name': 'Название типа',
    }

class EquipmentModelView(ModelView):
    column_labels = {
        'id': 'ID',
        'name': 'Наименование модели',
        'brand': 'Бренд',
        'equipment_type': 'Тип оборудования',
        'processor': 'Процессор',
        'ram_gb': 'ОЗУ (ГБ)',
        'storage_gb': 'Хранилище (ГБ)',
        'storage_type': 'Тип накопителя',
        'os': 'Операционная система',
        'screen_size': 'Диагональ экрана',
        'extra_specs': 'Дополнительные характеристики',
    }

class LocationView(ModelView):
    column_labels = {
        'id': 'ID',
        'name': 'Наименование',
        'location_type': 'Тип места',
        'parent': 'Находится внутри',
        'description': 'Описание',
        'full_path': 'Полный путь',
    }

class DepartmentView(ModelView):
    column_labels = {
        'id': 'ID',
        'name': 'Наименование подразделения',
        'parent': 'Головное подразделение',
        'short_name': 'Краткое наименование',
        'code': 'Код подразделения',
        'full_path': 'Полный путь',
    }

class EmployeeView(ModelView):
    column_labels = {
        'id': 'ID',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'middle_name': 'Отчество',
        'email': 'Email',
        'phone': 'Телефон',
        'department': 'Подразделение',
        'position': 'Должность',
        'is_active': 'Активен',
        'date_joined': 'Дата приёма',
        'date_left': 'Дата увольнения',
        'full_name': 'Полное имя',
    }

class EquipmentView(ModelView):
    column_labels = {
        'id': 'ID',
        'inventory_number': 'Инвентарный номер',
        'serial_number': 'Серийный номер',
        'model': 'Модель',
        'location': 'Место установки',
        'responsible_department': 'Ответственное подразделение',
        'department': 'Фактическое подразделение',
        'current_user': 'Текущий пользователь',
        'delivery_date': 'Дата поставки',
        'commissioning_date': 'Дата ввода в эксплуатацию',
        'status': 'Статус',
        'description': 'Примечание',
        'full_location_path': 'Полный путь места',
        'responsible_department_name': 'Ответственное подразделение',
    }

class ApprovalView(ModelView):
    column_labels = {
        'id': 'ID',
        'log_entry': 'Запись журнала',
        'department': 'Согласующее подразделение',
        'is_approved': 'Согласовано',
        'approved_by': 'Кто согласовал',
        'approved_at': 'Дата согласования',
        'comment': 'Комментарий',
        'required': 'Обязательное согласование',
    }

# ---------- КАСТОМНЫЙ VIEW ДЛЯ ЛОГОВ (ОСТАВЛЯЕМ ОДИН РАЗ) ----------
class EquipmentLogView(ModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            fill_old_values_on_create(model)
        return super().on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        if is_created:
            update_equipment_from_log(model)
        return super().after_model_change(form, model, is_created)

    column_labels = {
        'id': 'ID',
        'equipment': 'Оборудование',
        'action': 'Действие',
        'date': 'Дата и время',
        'initiator': 'Инициатор',
        'old_location': 'Прежнее место',
        'new_location': 'Новое место',
        'old_department': 'Прежнее подразделение',
        'new_department': 'Новое подразделение',
        'old_responsible_department': 'Прежний ответственный отдел',
        'new_responsible_department': 'Новый ответственный отдел',
        'old_status': 'Прежний статус',
        'new_status': 'Новый статус',
        'old_user': 'Прежний пользователь',
        'new_user': 'Новый пользователь',
        'description': 'Комментарий',
    }

# ---------- РЕГИСТРАЦИЯ МОДЕЛЕЙ ----------
admin.add_view(EquipmentTypeView(EquipmentType, name='Типы оборудования'))
admin.add_view(EquipmentModelView(EquipmentModel, name='Модели оборудования'))
admin.add_view(LocationView(Location, name='Места установки'))
admin.add_view(DepartmentView(Department, name='Подразделения'))
admin.add_view(EmployeeView(Employee, name='Сотрудники'))
admin.add_view(EquipmentView(Equipment, name='Оборудование'))
admin.add_view(EquipmentLogView(EquipmentLog, name='Журнал операций'))
admin.add_view(ApprovalView(Approval, name='Согласования'))

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