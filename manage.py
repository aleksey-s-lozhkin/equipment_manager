#!/usr/bin/env python
"""
Утилита для управления миграциями peewee-migrate
Использование:
    python manage.py create_initial   - Создать начальную миграцию из моделей
    python manage.py migrate          - Применить все миграции
    python manage.py rollback         - Откатить последнюю миграцию
    python manage.py list             - Показать все миграции
    python manage.py create <name>    - Создать пустую миграцию
"""

import sys
import os
from peewee_migrate import Router
from models import db, BaseModel

# Путь к папке с миграциями
MIGRATIONS_DIR = 'migrations'

def create_initial_migration():
    """Создаёт миграцию из всех существующих моделей"""

    # Получаем все модели, наследующие от BaseModel
    import models
    models_list = []

    for name, obj in models.__dict__.items():
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj != BaseModel:
            models_list.append(obj)

    if not models_list:
        print("❌ Модели не найдены")
        return

    print(f"🔍 Найдено моделей: {len(models_list)}")
    for m in models_list:
        print(f"  - {m.__name__}")

    # Создаём миграцию
    router = Router(db, migrate_dir=MIGRATIONS_DIR)
    router.create('initial')

    print("\n✅ Миграция 'initial' создана")
    print(f"📝 Файл: {MIGRATIONS_DIR}/001_initial.py")
    print("\n⚠️ ВАЖНО: Отредактируйте файл миграции и добавьте модели:")
    print("   from models import EquipmentType, EquipmentModel, ...")
    print("   database.create_tables([EquipmentType, EquipmentModel, ...])")

def main():
    # Создаём папку для миграций, если её нет
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)
        print(f"📁 Создана папка {MIGRATIONS_DIR}/")

    router = Router(db, migrate_dir=MIGRATIONS_DIR)

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == 'create_initial':
        create_initial_migration()

    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Укажите имя миграции: python manage.py create add_field")
            return
        name = sys.argv[2]
        router.create(name)
        print(f"✅ Миграция '{name}' создана")

    elif command == 'migrate':
        router.run()
        print("✅ Все миграции применены")

    elif command == 'rollback':
        router.rollback()
        print("✅ Откат выполнен")

    elif command == 'list':
        all_migrations = router.get_all_migrations()
        applied = router.get_applied_migrations()

        print("\n📋 Список миграций:")
        for mig in all_migrations:
            status = "✅ Применена" if mig in applied else "⏳ Ожидает"
            print(f"  {mig} - {status}")

        if not all_migrations:
            print("  (Нет миграций)")
        print()

    else:
        print(f"❌ Неизвестная команда: {command}")
        print_help()

def print_help():
    print("Использование:")
    print("  python manage.py create_initial   - Создать начальную миграцию из моделей")
    print("  python manage.py migrate          - Применить все миграции")
    print("  python manage.py rollback         - Откатить последнюю миграцию")
    print("  python manage.py list             - Показать все миграции")
    print("  python manage.py create <name>    - Создать пустую миграцию")

if __name__ == '__main__':
    # Подключаемся к БД перед запуском
    db.connect()
    main()
    db.close()