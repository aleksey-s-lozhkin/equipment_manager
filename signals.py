from peewee import *
from models import EquipmentLog, Equipment
from datetime import datetime


def fill_old_values_on_create(log_instance):
    """Перед созданием лога подставляем текущие значения"""
    if log_instance.id:  # Только для новых записей
        return

    equipment = log_instance.equipment

    # Заполняем old_location, если не указан и action связан с перемещением
    if not log_instance.old_location and log_instance.action in ['move', 'transfer']:
        log_instance.old_location = equipment.location

    # Заполняем old_department
    if not log_instance.old_department and log_instance.action in ['move', 'transfer']:
        log_instance.old_department = equipment.department

    # Заполняем old_responsible_department
    if not log_instance.old_responsible_department:
        log_instance.old_responsible_department = equipment.responsible_department

    # Заполняем old_status
    if not log_instance.old_status and log_instance.action == 'status_change':
        log_instance.old_status = equipment.status

    # Заполняем old_user
    if not log_instance.old_user and log_instance.action == 'transfer':
        log_instance.old_user = equipment.current_user


def update_equipment_from_log(log_instance):
    """После создания записи обновляем Equipment"""
    equipment = log_instance.equipment
    needs_save = False
    update_fields = []

    # Обработка перемещения
    if log_instance.action == 'move' and log_instance.new_location:
        equipment.location = log_instance.new_location
        needs_save = True
        update_fields.append('location')

    # Обработка передачи в другой отдел
    if log_instance.action == 'move' and log_instance.new_department:
        equipment.department = log_instance.new_department
        needs_save = True
        update_fields.append('department')

    # Смена ответственного отдела
    if log_instance.new_responsible_department:
        equipment.responsible_department = log_instance.new_responsible_department
        needs_save = True
        update_fields.append('responsible_department')

    # Смена статуса
    if log_instance.action == 'status_change' and log_instance.new_status:
        equipment.status = log_instance.new_status
        needs_save = True
        update_fields.append('status')

    # Смена пользователя
    if log_instance.action == 'transfer' and log_instance.new_user:
        equipment.current_user = log_instance.new_user
        needs_save = True
        update_fields.append('current_user')

    if needs_save:
        equipment.save(only=update_fields)


def generate_inventory_number(equipment_instance):
    """Автогенерация инвентарного номера"""
    if not equipment_instance.inventory_number:
        year = datetime.now().year
        last = Equipment.select().where(
            Equipment.inventory_number.startswith(f'СВТ-{year}-')
        ).count()
        equipment_instance.inventory_number = f"СВТ-{year}-{last + 1:05d}"


# Hook для EquipmentLog (используем в app.py при создании)
def setup_signals():
    """Регистрируем хуки для моделей"""
    pass