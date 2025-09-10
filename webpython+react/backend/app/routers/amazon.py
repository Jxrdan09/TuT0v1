from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import (
    AmazonCardCheck, AmazonCardResult, UserCookieCreate, 
    UserCookie, CardCheck
)
from ..auth import get_current_active_user
from ..gateways.amazon.amazon_gateway import AmazonGateway

router = APIRouter(prefix="/amazon", tags=["amazon-gateway"])

@router.post("/cookie", response_model=dict)
async def save_amazon_cookie(
    cookie_data: UserCookieCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Guardar cookie de Amazon para el usuario"""
    
    if cookie_data.gateway_type != "amazon":
        raise HTTPException(
            status_code=400,
            detail="Tipo de gateway debe ser 'amazon'"
        )
    
    gateway = AmazonGateway(db)
    success, message = await gateway.save_cookie(current_user.id, cookie_data.cookie_data)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message, "success": True}

@router.get("/cookie", response_model=UserCookie)
async def get_amazon_cookie(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener cookie de Amazon del usuario"""
    
    gateway = AmazonGateway(db)
    cookie_data = gateway.get_cookie(current_user.id)
    
    if not cookie_data:
        raise HTTPException(
            status_code=404,
            detail="No hay cookie configurada para Amazon"
        )
    
    # Buscar el registro en la base de datos
    cookie_record = db.query(UserCookie).filter(
        UserCookie.user_id == current_user.id,
        UserCookie.gateway_type == "amazon",
        UserCookie.is_active == True
    ).first()
    
    if not cookie_record:
        raise HTTPException(
            status_code=404,
            detail="No hay cookie configurada para Amazon"
        )
    
    return cookie_record

@router.post("/check-card", response_model=AmazonCardResult)
async def check_amazon_card(
    card_check: AmazonCardCheck,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verificar una tarjeta en Amazon"""
    
    gateway = AmazonGateway(db)
    result = await gateway.check_card(current_user.id, card_check.card_data)
    
    return result

@router.post("/check-cards", response_model=List[AmazonCardResult])
async def check_multiple_amazon_cards(
    cards: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verificar múltiples tarjetas en Amazon"""
    
    if len(cards) > 15:
        raise HTTPException(
            status_code=400,
            detail="Máximo 15 tarjetas por consulta"
        )
    
    gateway = AmazonGateway(db)
    results = await gateway.check_multiple_cards(current_user.id, cards)
    
    return results

@router.get("/history", response_model=List[CardCheck])
async def get_amazon_card_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de verificaciones de Amazon"""
    
    if limit > 100:
        limit = 100
    
    gateway = AmazonGateway(db)
    history = gateway.get_user_card_history(current_user.id, limit)
    
    return history

@router.get("/stats", response_model=dict)
async def get_amazon_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de Amazon del usuario"""
    
    gateway = AmazonGateway(db)
    stats = gateway.get_user_stats(current_user.id)
    
    return stats

@router.delete("/cookie")
async def delete_amazon_cookie(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar cookie de Amazon del usuario"""
    
    cookie_record = db.query(UserCookie).filter(
        UserCookie.user_id == current_user.id,
        UserCookie.gateway_type == "amazon"
    ).first()
    
    if not cookie_record:
        raise HTTPException(
            status_code=404,
            detail="No hay cookie configurada para Amazon"
        )
    
    cookie_record.is_active = False
    db.commit()
    
    return {"message": "Cookie eliminada exitosamente"}
