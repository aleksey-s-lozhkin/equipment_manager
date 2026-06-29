import json

from peewee import *
from datetime import datetime

# ---------- БАЗА ДАННЫХ ----------
db = SqliteDatabase('equipment.db')


# ---------- БАЗОВАЯ МОДЕЛЬ ----------
class BaseModel(Model):
    """Базовый класс для всех моделей"""

    class Meta:
        database = db


# ---------- КАСТОМНОЕ ПОЛЕ ДЛЯ JSON ----------
class JSONField(TextField):
    """Поле для хранения JSON в TextField"""

    def db_value(self, value):
        """Преобразует Python-объект в строку для БД"""
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def python_value(self, value):
        """Преобразует строку из БД в Python-объект"""
        if value is None or value == '':
            return {}
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}


# ---------- EquipmentType ----------
class EquipmentType(BaseModel):
    name = CharField(max_length=100, unique=True, verbose_name="Тип оборудования")

    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"
        ordering = ['name']

    def __str__(self):
        return self.name


# ---------- EquipmentModel ----------
class EquipmentModel(BaseModel):
    name = CharField(max_length=200, verbose_name="Наименование модели")
    brand = CharField(max_length=100, verbose_name="Бренд")
    equipment_type = ForeignKeyField(EquipmentType, backref='models', on_delete='RESTRICT')

    # Технические характеристики
    processor = CharField(max_length=100, null=True, verbose_name="Процессор")
    ram_gb = IntegerField(null=True, verbose_name="ОЗУ (ГБ)")
    storage_gb = IntegerField(null=True, verbose_name="Хранилище (ГБ)")
    storage_type = CharField(max_length=50, null=True, verbose_name="Тип накопителя")
    os = CharField(max_length=50, null=True, verbose_name="Операционная система")
    screen_size = DecimalField(max_digits=4, decimal_places=1, null=True, verbose_name="Диагональ экрана")

    # Гибкое поле
    extra_specs = JSONField(default={}, verbose_name="Дополнительные характеристики")

    class Meta:
        verbose_name = "Модель оборудования"
        verbose_name_plural = "Модели оборудования"
        ordering = ['brand', 'name']
        indexes = (
            (('brand', 'name'), True),  # unique together
        )

    def __str__(self):
        return f"{self.brand} {self.name}"


# ---------- Location (иерархия) ----------
class Location(BaseModel):
    LOCATION_TYPES = [
        ('territory', 'Территория'),
        ('workshop', 'Цех'),
        ('building', 'Здание'),
        ('floor', 'Этаж'),
        ('room', 'Помещение'),
        ('rack', 'Шкаф'),
        ('container', 'Контейнер'),
        ('outdoor', 'Открытая площадка'),
    ]

    name = CharField(max_length=200, verbose_name="Наименование")
    location_type = CharField(max_length=20, choices=LOCATION_TYPES, verbose_name="Тип места")
    parent = ForeignKeyField('self', backref='children', null=True, on_delete='CASCADE')
    description = TextField(null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Место установки"
        verbose_name_plural = "Места установки"
        ordering = ['location_type', 'name']

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        """Полный путь от корня"""
        ancestors = []
        node = self
        while node:
            ancestors.append(node.name)
            node = node.parent
        return " → ".join(reversed(ancestors))

    def get_descendants(self, include_self=False):
        """Получить все дочерние узлы (рекурсивно)"""
        result = [self] if include_self else []
        for child in self.children:
            result.extend(child.get_descendants(include_self=True))
        return result


# ---------- Department (иерархия) ----------
class Department(BaseModel):
    name = CharField(max_length=200, unique=True, verbose_name="Наименование подразделения")
    parent = ForeignKeyField('self', backref='children', null=True, on_delete='CASCADE')
    short_name = CharField(max_length=50, null=True, verbose_name="Краткое наименование")
    code = CharField(max_length=20, unique=True, null=True, verbose_name="Код подразделения")

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        ancestors = []
        node = self
        while node:
            ancestors.append(node.name)
            node = node.parent
        return " → ".join(reversed(ancestors))


# ---------- Employee ----------
class Employee(BaseModel):
    first_name = CharField(max_length=100, verbose_name="Имя")
    last_name = CharField(max_length=100, verbose_name="Фамилия")
    middle_name = CharField(max_length=100, null=True, verbose_name="Отчество")
    email = CharField(max_length=255, unique=True, verbose_name="Email")
    phone = CharField(max_length=20, null=True, verbose_name="Телефон")
    department = ForeignKeyField(Department, backref='employees', on_delete='RESTRICT')
    position = CharField(max_length=100, null=True, verbose_name="Должность")
    is_active = BooleanField(default=True, verbose_name="Активен")
    date_joined = DateField(default=datetime.now, verbose_name="Дата приёма")
    date_left = DateField(null=True, verbose_name="Дата увольнения")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    @property
    def full_name(self):
        return self.__str__()


# ---------- Equipment ----------
class Equipment(BaseModel):
    """Средство вычислительной техники (СВТ)"""
    STATUS_CHOICES = [
        ('in_use', 'В эксплуатации'),
        ('reserve', 'В резерве'),
        ('repair', 'В ремонте'),
        ('disposed', 'Списано'),
        ('lost', 'Утеряно'),
    ]

    # Идентификаторы
    inventory_number = CharField(
        max_length=50,
        null=True,  # ← Разрешаем NULL
        unique=True,  # ← Если указан, должен быть уникальным
        verbose_name="Инвентарный номер"
    )
    serial_number = CharField(
        max_length=100,
        unique=True,
        verbose_name="Серийный номер"
    )

    # Связи
    model = ForeignKeyField(EquipmentModel, backref='equipment', on_delete='RESTRICT')
    location = ForeignKeyField(Location, backref='equipment', on_delete='RESTRICT')

    # Ответственность
    responsible_department = ForeignKeyField(Department, backref='equipment_responsible', on_delete='RESTRICT')
    department = ForeignKeyField(Department, backref='equipment_actual', on_delete='RESTRICT')
    current_user = ForeignKeyField(Employee, backref='equipment_in_use', null=True, on_delete='SET NULL')

    # Даты
    delivery_date = DateField(  # ← Переименовано с purchase_date
        null=True,
        verbose_name="Дата поставки"
    )
    commissioning_date = DateField(
        null=True,
        verbose_name="Дата ввода в эксплуатацию"
    )

    # Статус
    status = CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_use',
        verbose_name="Статус"
    )

    # Дополнительно
    description = TextField(
        null=True,
        verbose_name="Примечание"
    )

    class Meta:
        verbose_name = "Средство вычислительной техники"
        verbose_name_plural = "Средства вычислительной техники"
        ordering = ['inventory_number']

    def __str__(self):
        return f"{self.inventory_number or 'Без инв.номера'} - {self.model.name}"

    @property
    def full_location_path(self):
        return self.location.full_path if self.location else "Не указано"

    @property
    def responsible_department_name(self):
        return self.responsible_department.name if self.responsible_department else "Не указан"


# ---------- EquipmentLog ----------
class EquipmentLog(BaseModel):
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('move', 'Перемещение'),
        ('repair', 'Ремонт'),
        ('maintenance', 'Техобслуживание'),
        ('disposal', 'Списание'),
        ('transfer', 'Передача сотруднику'),
        ('inventory', 'Инвентаризация'),
        ('status_change', 'Смена статуса'),
    ]

    equipment = ForeignKeyField(Equipment, backref='logs', on_delete='CASCADE')
    action = CharField(max_length=20, choices=ACTION_CHOICES)
    date = DateTimeField(default=datetime.now)
    initiator = ForeignKeyField(Employee, backref='initiated_logs', on_delete='RESTRICT')

    # Трекинг местоположения
    old_location = ForeignKeyField(Location, backref='logs_as_old', null=True, on_delete='SET NULL')
    new_location = ForeignKeyField(Location, backref='logs_as_new', null=True, on_delete='SET NULL')

    # Трекинг подразделений
    old_department = ForeignKeyField(Department, backref='logs_as_old_dept', null=True, on_delete='SET NULL')
    new_department = ForeignKeyField(Department, backref='logs_as_new_dept', null=True, on_delete='SET NULL')

    # Трекинг ответственного отдела
    old_responsible_department = ForeignKeyField(Department, backref='logs_as_old_responsible', null=True,
                                                 on_delete='SET NULL')
    new_responsible_department = ForeignKeyField(Department, backref='logs_as_new_responsible', null=True,
                                                 on_delete='SET NULL')

    # Трекинг статуса
    old_status = CharField(max_length=20, null=True)
    new_status = CharField(max_length=20, null=True)

    # Трекинг пользователя
    old_user = ForeignKeyField(Employee, backref='logs_as_old_user', null=True, on_delete='SET NULL')
    new_user = ForeignKeyField(Employee, backref='logs_as_new_user', null=True, on_delete='SET NULL')

    description = TextField(null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал операций"
        ordering = ['-date']
        indexes = (
            (('equipment', 'action'), False),
            (('date',), False),
        )

    def __str__(self):
        return f"{self.equipment} - {self.get_action_display()} ({self.date.strftime('%Y-%m-%d %H:%M')})"

    def get_action_display(self):
        """Возвращает человекочитаемое название действия"""
        choices = dict(self.ACTION_CHOICES)
        return choices.get(self.action, self.action)


# ---------- 8. Approval ----------
class Approval(BaseModel):
    log_entry = ForeignKeyField(EquipmentLog, backref='approvals', on_delete='CASCADE')
    department = ForeignKeyField(Department, backref='approvals', on_delete='CASCADE')
    is_approved = BooleanField(default=False)
    approved_by = ForeignKeyField(Employee, backref='approved_logs', null=True, on_delete='SET NULL')
    approved_at = DateTimeField(null=True)
    comment = TextField(null=True)
    required = BooleanField(default=False)

    class Meta:
        verbose_name = "Согласование"
        verbose_name_plural = "Согласования"
        ordering = ['-approved_at']

    def __str__(self):
        status = "✅ Согласовано" if self.is_approved else "⏳ Ожидает"
        return f"{self.log_entry} - {status}"