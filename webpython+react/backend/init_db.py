#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear el primer usuario administrador
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, UserKey
from app.auth import get_password_hash
from app.config import settings
from sqlalchemy.orm import sessionmaker

def init_database():
    """Crear todas las tablas"""
    print("Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def create_admin_user():
    """Crear usuario administrador inicial"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            print("⚠️  Ya existe un usuario administrador")
            return
        
        # Crear admin
        admin_user = User(
            email=settings.admin_email,
            username="admin",
            hashed_password=get_password_hash(settings.admin_password),
            telegram_id="123456789",  # ID por defecto
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Usuario administrador creado:")
        print(f"   Email: {settings.admin_email}")
        print(f"   Username: admin")
        print(f"   Password: {settings.admin_password}")
        print(f"   Telegram ID: 123456789")
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_keys():
    """Crear algunas keys de ejemplo"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Crear keys de ejemplo
        sample_keys = [
            "KEY-2024-001",
            "KEY-2024-002", 
            "KEY-2024-003"
        ]
        
        for key_value in sample_keys:
            existing_key = db.query(UserKey).filter(UserKey.key == key_value).first()
            if not existing_key:
                key = UserKey(key=key_value, user_id=None)  # user_id será None hasta que se use
                db.add(key)
        
        db.commit()
        print(f"✅ {len(sample_keys)} keys de ejemplo creadas")
        
    except Exception as e:
        print(f"❌ Error creando keys: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🚀 Inicializando base de datos...")
    print("=" * 50)
    
    init_database()
    create_admin_user()
    create_sample_keys()
    
    print("=" * 50)
    print("✅ Inicialización completada")
    print("\n📝 Próximos pasos:")
    print("1. Ejecutar el backend: python run.py")
    print("2. Ejecutar el frontend: cd ../frontend && npm start")
    print("3. Acceder a http://localhost:3000")
    print("4. Iniciar sesión con las credenciales del admin")

if __name__ == "__main__":
    main()
