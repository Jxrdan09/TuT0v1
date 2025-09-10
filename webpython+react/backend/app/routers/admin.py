from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, UserKey, Script, ScriptExecution, Gateway
from ..schemas import (
    User as UserSchema, UserKeyCreate, UserKey as UserKeySchema,
    GatewayCreate, GatewayUpdate, Gateway as GatewaySchema
)
from ..auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

# Gestión de usuarios
@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los usuarios"""
    users = db.query(User).all()
    return users

@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activar/desactivar usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"Usuario {'activado' if user.is_active else 'desactivado'} exitosamente"}

@router.put("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Dar/quitar permisos de admin"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes modificar tus propios permisos")
    
    user.is_admin = not user.is_admin
    db.commit()
    
    return {"message": f"Permisos de admin {'otorgados' if user.is_admin else 'revocados'} exitosamente"}

# Gestión de keys
@router.post("/keys", response_model=UserKeySchema)
async def create_key(
    key_data: UserKeyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear nueva key de registro"""
    
    # Verificar que la key no exista
    existing_key = db.query(UserKey).filter(UserKey.key == key_data.key).first()
    if existing_key:
        raise HTTPException(status_code=400, detail="La key ya existe")
    
    # Permitir duración personalizada en días
    duration_days = getattr(key_data, 'duration_days', 30) or 30
    db_key = UserKey(key=key_data.key, duration_days=duration_days)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return db_key

@router.get("/keys", response_model=List[UserKeySchema])
async def get_all_keys(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las keys"""
    keys = db.query(UserKey).all()
    return keys

@router.put("/keys/{key_id}/toggle-status")
async def toggle_key_status(
    key_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activar/desactivar key"""
    key = db.query(UserKey).filter(UserKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key no encontrada")
    
    key.is_active = not key.is_active
    db.commit()
    
    return {"message": f"Key {'activada' if key.is_active else 'desactivada'} exitosamente"}

@router.post("/keys/{key_id}/renew", response_model=UserKeySchema)
async def renew_subscription_with_key(
    key_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Renovar suscripción de un usuario usando una key asignada (suma días)."""
    key = db.query(UserKey).filter(UserKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key no encontrada")

    if not key.user_id:
        raise HTTPException(status_code=400, detail="La key no está asignada a ningún usuario")

    user = db.query(User).filter(User.id == key.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para esta key")

    from datetime import datetime, timedelta
    now = datetime.utcnow()
    base_date = user.subscription_expires_at if user.subscription_expires_at and user.subscription_expires_at > now else now
    user.subscription_expires_at = base_date + timedelta(days=key.duration_days or 30)
    key.expires_at = user.subscription_expires_at
    db.commit()
    db.refresh(key)
    return key

@router.post("/users/{user_id}/extend", response_model=UserSchema)
async def extend_user_subscription(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Extender suscripción de un usuario directamente por N días."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    from datetime import datetime, timedelta
    now = datetime.utcnow()
    base_date = user.subscription_expires_at if user.subscription_expires_at and user.subscription_expires_at > now else now
    user.subscription_expires_at = base_date + timedelta(days=max(1, days))
    db.commit()
    db.refresh(user)
    return user

@router.delete("/keys/{key_id}")
async def delete_key(
    key_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar key"""
    key = db.query(UserKey).filter(UserKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key no encontrada")
    
    db.delete(key)
    db.commit()
    
    return {"message": "Key eliminada exitosamente"}

# Gestión de gateways
@router.post("/gateways", response_model=GatewaySchema)
async def create_gateway(
    gateway_data: GatewayCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo gateway"""
    
    db_gateway = Gateway(
        name=gateway_data.name,
        type=gateway_data.type,
        config=gateway_data.config
    )
    
    db.add(db_gateway)
    db.commit()
    db.refresh(db_gateway)
    
    return db_gateway

@router.get("/gateways", response_model=List[GatewaySchema])
async def get_all_gateways(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los gateways"""
    gateways = db.query(Gateway).all()
    return gateways

@router.put("/gateways/{gateway_id}", response_model=GatewaySchema)
async def update_gateway(
    gateway_id: int,
    gateway_update: GatewayUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualizar gateway"""
    
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway no encontrado")
    
    if gateway_update.name is not None:
        gateway.name = gateway_update.name
    if gateway_update.type is not None:
        gateway.type = gateway_update.type
    if gateway_update.config is not None:
        gateway.config = gateway_update.config
    if gateway_update.is_active is not None:
        gateway.is_active = gateway_update.is_active
    
    db.commit()
    db.refresh(gateway)
    
    return gateway

@router.delete("/gateways/{gateway_id}")
async def delete_gateway(
    gateway_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar gateway"""
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway no encontrado")
    
    db.delete(gateway)
    db.commit()
    
    return {"message": "Gateway eliminado exitosamente"}

# Estadísticas del sistema
@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del sistema"""
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_scripts = db.query(Script).filter(Script.is_active == True).count()
    total_executions = db.query(ScriptExecution).count()
    active_keys = db.query(UserKey).filter(UserKey.is_active == True).count()
    total_gateways = db.query(Gateway).filter(Gateway.is_active == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_scripts": total_scripts,
        "total_executions": total_executions,
        "active_keys": active_keys,
        "total_gateways": total_gateways
    }
