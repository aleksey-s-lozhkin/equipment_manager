# migrations/001_initial.py
from peewee_migrate import Migrator
import peewee as pw

# Импортируем ВСЕ модели из models.py
from models import (
    EquipmentType, EquipmentModel, Location, Department,
    Employee, Equipment, EquipmentLog, Approval
)


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Создаём все таблицы и добавляем начальные данные"""
    
    # 1. СОЗДАЁМ ТАБЛИЦЫ (в правильном порядке — сначала таблицы без внешних ключей)
    print("📊 Создаём таблицы...")
    
    database.create_tables([
        EquipmentType,      # Типы оборудования
        EquipmentModel,     # Модели оборудования (зависит от EquipmentType)
        Location,           # Места установки (самореференция)
        Department,         # Подразделения (самореференция)
        Employee,           # Сотрудники (зависит от Department)
        Equipment,          # Оборудование (зависит от многих)
        EquipmentLog,       # Журнал (зависит от Equipment)
        Approval,           # Согласования (зависит от EquipmentLog)
    ])
    
    print("✅ Таблицы созданы")
    
    # 2. ДОБАВЛЯЕМ НАЧАЛЬНЫЕ ДАННЫЕ (только если не в режиме fake)
    if not fake:
        print("📦 Добавляем начальные данные...")
        
        # --- Типы оборудования ---
        types = ['Ноутбук', 'Системный блок', 'Монитор', 'Принтер', 'Сервер', 'Сетевое оборудование']
        for type_name in types:
            EquipmentType.get_or_create(name=type_name)
        print(f"  ✅ Добавлено {len(types)} типов оборудования")
        
        # --- Корневое подразделение ---
        root_dept, created = Department.get_or_create(
            name="Аппарат управления",
            defaults={
                'short_name': 'АУП',
                'code': '001'
            }
        )
        print(f"  ✅ Создано подразделение: {root_dept}")
        
        # --- Дочерние подразделения ---
        it_dept, _ = Department.get_or_create(
            name="САСУ",
            defaults={
                'parent': root_dept,
                'short_name': 'ASU',
                'code': '002'
            }
        )
        print(f"  ✅ Создано подразделение: {it_dept}")
        
        hr_dept, _ = Department.get_or_create(
            name="СКИПиА, ТМ и М",
            defaults={
                'parent': root_dept,
                'short_name': 'KIP',
                'code': '003'
            }
        )
        print(f"  ✅ Создано подразделение: {hr_dept}")
        
        # --- Корневое место ---
        root_location, _ = Location.get_or_create(
            name="Производственно-эксплуатационный блок",
            defaults={
                'location_type': 'building',
                'description': 'ПЭБ'
            }
        )
        print(f"  ✅ Создано место: {root_location}")
        
        # --- Дочерние места ---
        office_1, _ = Location.get_or_create(
            name="Кабинет 205",
            defaults={
                'location_type': 'room',
                'parent': root_location,
                'description': 'Начальник АСУ'
            }
        )
        print(f"  ✅ Создано место: {office_1}")
        
        office_2, _ = Location.get_or_create(
            name="Кабинет 206",
            defaults={
                'location_type': 'room',
                'parent': root_location,
                'description': 'Инженеры АСУ'
            }
        )
        print(f"  ✅ Создано место: {office_2}")
        
        # --- Администратор системы ---
        admin_user, _ = Employee.get_or_create(
            email='admin@pik.com',
            defaults={
                'first_name': 'Системный',
                'last_name': 'Администратор',
                'middle_name': '',
                'department': it_dept,
                'position': 'Главный администратор',
                'is_active': True,
                'phone': '52-202'
            }
        )
        print(f"  ✅ Создан пользователь: {admin_user}")
        
        # --- Обычный сотрудник ---
        hr_user, _ = Employee.get_or_create(
            email='ingener_asu@pik.com',
            defaults={
                'first_name': 'Анна',
                'last_name': 'Иванова',
                'middle_name': 'Петровна',
                'department': hr_dept,
                'position': 'Менеджер по персоналу',
                'is_active': True,
                'phone': '52-XXX'
            }
        )
        print(f"  ✅ Создан пользователь: {hr_user}")
        
        print("✅ Начальные данные добавлены!")


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Откатываем миграцию — удаляем все таблицы"""
    
    print("🗑️ Удаляем все таблицы...")
    
    # Удаляем в обратном порядке (сначала те, у кого есть внешние ключи)
    database.drop_tables([
        Approval,           # Согласования
        EquipmentLog,       # Журнал
        Equipment,          # Оборудование
        Employee,           # Сотрудники
        Department,         # Подразделения
        Location,           # Места
        EquipmentModel,     # Модели
        EquipmentType,      # Типы
    ])
    
    print("✅ Все таблицы удалены")