from flask import Flask, send_from_directory
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
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'

# ---------- ОТКЛЮЧАЕМ ТЕМУ ИЗ CDN ----------
app.config['FLASK_ADMIN_SWATCH'] = None

# ---------- МАРШРУТЫ ДЛЯ ЛОКАЛЬНОЙ СТАТИКИ ----------
@app.route('/static/bootstrap/css/<path:filename>')
def serve_bootstrap_css(filename):
    return send_from_directory('static/bootstrap/css', filename)

@app.route('/static/bootstrap/js/<path:filename>')
def serve_bootstrap_js(filename):
    return send_from_directory('static/bootstrap/js', filename)

@app.route('/static/font-awesome/css/<path:filename>')
def serve_fontawesome_css(filename):
    return send_from_directory('static/font-awesome/css', filename)

# ---------- Babel ----------
babel = Babel(app)

# ---------- КАСТОМНАЯ ГЛАВНАЯ СТРАНИЦА АДМИНКИ ----------
class MyAdminIndexView(AdminIndexView):
    """Кастомная главная страница админки"""

    def render(self, template, **kwargs):
        # 1. Общая статистика
        total_equipment = Equipment.select().count()
        in_use = Equipment.select().where(Equipment.status == 'in_use').count()
        in_repair = Equipment.select().where(Equipment.status == 'repair').count()
        in_reserve = Equipment.select().where(Equipment.status == 'reserve').count()
        without_user = Equipment.select().where(Equipment.current_user.is_null()).count()

        # 2. По типам оборудования
        from peewee import fn
        by_type = []
        for eq_type in EquipmentType.select():
            count = Equipment.select().join(EquipmentModel).where(
                EquipmentModel.equipment_type == eq_type
            ).count()
            if count > 0:
                by_type.append({
                    'name': eq_type.name,
                    'count': count
                })

        # 3. Последние 5 операций
        recent_logs = EquipmentLog.select().order_by(EquipmentLog.date.desc()).limit(5)

        stats = {
            'total_equipment': total_equipment,
            'in_use': in_use,
            'in_repair': in_repair,
            'in_reserve': in_reserve,
            'without_user': without_user,
            'by_type': by_type,
            'recent_logs': recent_logs,
            # Старые поля для совместимости
            'equipment_types': EquipmentType.select().count(),
            'equipment_models': EquipmentModel.select().count(),
            'locations': Location.select().count(),
            'departments': Department.select().count(),
            'employees': Employee.select().count(),
            'equipment': total_equipment,
            'logs': EquipmentLog.select().count(),
        }
        return super().render(template, stats=stats, **kwargs)

# ---------- НАСТРОЙКА АДМИНКИ ----------
admin = Admin(
    app,
    name='Управление оборудованием',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView(),
    base_template='admin/master.html'
)

# ---------- КАСТОМНЫЕ VIEW ДЛЯ РУССКИХ НАЗВАНИЙ ----------

class EquipmentTypeView(ModelView):
    column_labels = {
        'id': 'ID',
        'name': 'Название типа',
    }

    form_args = {
        'name': {'label': 'Название типа'},
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

    form_args = {
        'name': {'label': 'Наименование модели'},
        'brand': {'label': 'Бренд'},
        'equipment_type': {'label': 'Тип оборудования'},
        'processor': {'label': 'Процессор'},
        'ram_gb': {'label': 'ОЗУ (ГБ)'},
        'storage_gb': {'label': 'Хранилище (ГБ)'},
        'storage_type': {'label': 'Тип накопителя'},
        'os': {'label': 'Операционная система'},
        'screen_size': {'label': 'Диагональ экрана'},
        'extra_specs': {'label': 'Дополнительные характеристики'},
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

    form_args = {
        'name': {'label': 'Наименование'},
        'location_type': {'label': 'Тип места'},
        'parent': {'label': 'Находится внутри'},
        'description': {'label': 'Описание'},
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

    form_args = {
        'name': {'label': 'Наименование подразделения'},
        'parent': {'label': 'Головное подразделение'},
        'short_name': {'label': 'Краткое наименование'},
        'code': {'label': 'Код подразделения'},
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

    form_args = {
        'first_name': {'label': 'Имя'},
        'last_name': {'label': 'Фамилия'},
        'middle_name': {'label': 'Отчество'},
        'email': {'label': 'Email'},
        'phone': {'label': 'Телефон'},
        'department': {'label': 'Подразделение'},
        'position': {'label': 'Должность'},
        'is_active': {'label': 'Активен'},
        'date_joined': {'label': 'Дата приёма'},
        'date_left': {'label': 'Дата увольнения'},
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
    }

    form_args = {
        'inventory_number': {'label': 'Инвентарный номер'},
        'serial_number': {'label': 'Серийный номер'},
        'model': {'label': 'Модель'},
        'location': {'label': 'Место установки'},
        'responsible_department': {'label': 'Ответственное подразделение'},
        'department': {'label': 'Фактическое подразделение'},
        'current_user': {'label': 'Текущий пользователь'},
        'delivery_date': {'label': 'Дата поставки'},
        'commissioning_date': {'label': 'Дата ввода в эксплуатацию'},
        'status': {'label': 'Статус'},
        'description': {'label': 'Примечание'},
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

    form_args = {
        'log_entry': {'label': 'Запись журнала'},
        'department': {'label': 'Согласующее подразделение'},
        'is_approved': {'label': 'Согласовано'},
        'approved_by': {'label': 'Кто согласовал'},
        'approved_at': {'label': 'Дата согласования'},
        'comment': {'label': 'Комментарий'},
        'required': {'label': 'Обязательное согласование'},
    }

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

    form_args = {
        'equipment': {'label': 'Оборудование'},
        'action': {'label': 'Действие'},
        'date': {'label': 'Дата и время'},
        'initiator': {'label': 'Инициатор'},
        'old_location': {'label': 'Прежнее место'},
        'new_location': {'label': 'Новое место'},
        'old_department': {'label': 'Прежнее подразделение'},
        'new_department': {'label': 'Новое подразделение'},
        'old_responsible_department': {'label': 'Прежний ответственный отдел'},
        'new_responsible_department': {'label': 'Новый ответственный отдел'},
        'old_status': {'label': 'Прежний статус'},
        'new_status': {'label': 'Новый статус'},
        'old_user': {'label': 'Прежний пользователь'},
        'new_user': {'label': 'Новый пользователь'},
        'description': {'label': 'Комментарий'},
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