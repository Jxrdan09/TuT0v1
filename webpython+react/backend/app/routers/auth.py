from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import User, UserKey
from ..schemas import UserCreate, UserLogin, Token, User as UserSchema
from ..auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_active_user, get_current_admin_user
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserSchema)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario con validación de key"""
    
    # Verificar si el usuario ya existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso"
        )
    
    if db.query(User).filter(User.telegram_id == user_data.telegram_id).first():
        raise HTTPException(
            status_code=400,
            detail="El ID de Telegram ya está registrado"
        )
    
    # Verificar que la key sea válida
    valid_key = db.query(UserKey).filter(
        UserKey.key == user_data.key,
        UserKey.is_active == True
    ).first()
    
    if not valid_key:
        raise HTTPException(
            status_code=400,
            detail="Key inválida o inactiva"
        )
    
    # Crear usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        telegram_id=user_data.telegram_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Activar suscripción según duración de la key
    from datetime import datetime, timedelta
    subscription_days = valid_key.duration_days if getattr(valid_key, 'duration_days', None) is not None else 30
    db_user.subscription_expires_at = datetime.utcnow() + timedelta(days=subscription_days)

    # Marcar uso de la key sin eliminar: asignar al usuario, marcar como inactiva y registrar activación
    valid_key.is_active = False
    valid_key.user_id = db_user.id
    valid_key.activated_at = datetime.utcnow()
    valid_key.expires_at = db_user.subscription_expires_at

    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.post("/create-admin")
async def create_admin_user(
    email: str,
    password: str,
    username: str,
    telegram_id: str,
    db: Session = Depends(get_db)
):
    """Crear usuario administrador (solo para setup inicial)"""
    
    # Verificar si ya existe un admin
    existing_admin = db.query(User).filter(User.is_admin == True).first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario administrador"
        )
    
    # Crear admin
    hashed_password = get_password_hash(password)
    admin_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        telegram_id=telegram_id,
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return {"message": "Usuario administrador creado exitosamente"}
