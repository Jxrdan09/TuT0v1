from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Proxy
from ..auth import get_current_active_user, get_current_admin_user
from ..proxy_manager import ProxyManager

router = APIRouter(prefix="/proxies", tags=["proxies"])

@router.post("/load-from-file")
async def load_proxies_from_file(
    proxy_type: str = "http",
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Cargar proxies desde archivo TXT (solo admin)"""
    
    proxy_manager = ProxyManager(db)
    result = proxy_manager.load_proxies_from_file_to_db(proxy_type)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/upload-file")
async def upload_proxy_file(
    file: UploadFile = File(...),
    proxy_type: str = "http",
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Subir archivo de proxies (solo admin)"""
    
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .txt")
    
    try:
        content = await file.read()
        proxy_strings = content.decode('utf-8').strip().split('\n')
        
        # Filtrar líneas vacías y comentarios
        proxies = [line.strip() for line in proxy_strings if line.strip() and not line.strip().startswith('#')]
        
        if not proxies:
            raise HTTPException(status_code=400, detail="No se encontraron proxies válidos en el archivo")
        
        proxy_manager = ProxyManager(db)
        added_count = proxy_manager.save_proxies_to_database(proxies, proxy_type)
        
        return {
            "success": True,
            "message": f"Proxies cargados exitosamente",
            "added": added_count,
            "total": len(proxies)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(e)}")

@router.get("/", response_model=List[dict])
async def get_proxies(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de proxies (solo admin)"""
    
    proxies = db.query(Proxy).all()
    
    return [
        {
            "id": proxy.id,
            "proxy_string": proxy.proxy_string,
            "proxy_type": proxy.proxy_type,
            "is_active": proxy.is_active,
            "success_count": proxy.success_count,
            "failure_count": proxy.failure_count,
            "success_rate": proxy.success_rate,
            "last_used": proxy.last_used,
            "created_at": proxy.created_at
        }
        for proxy in proxies
    ]

@router.get("/stats")
async def get_proxy_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de proxies (solo admin)"""
    
    proxy_manager = ProxyManager(db)
    return proxy_manager.get_proxy_stats()

@router.post("/test-all")
async def test_all_proxies(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Probar todos los proxies (solo admin)"""
    
    proxy_manager = ProxyManager(db)
    result = await proxy_manager.test_all_proxies()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.put("/{proxy_id}/toggle")
async def toggle_proxy_status(
    proxy_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activar/desactivar proxy (solo admin)"""
    
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy no encontrado")
    
    proxy.is_active = not proxy.is_active
    db.commit()
    
    return {
        "message": f"Proxy {'activado' if proxy.is_active else 'desactivado'} exitosamente",
        "is_active": proxy.is_active
    }

@router.delete("/{proxy_id}")
async def delete_proxy(
    proxy_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar proxy (solo admin)"""
    
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy no encontrado")
    
    db.delete(proxy)
    db.commit()
    
    return {"message": "Proxy eliminado exitosamente"}

@router.post("/create-template")
async def create_proxy_template(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear archivo de plantilla para proxies (solo admin)"""
    
    proxy_manager = ProxyManager(db)
    message = proxy_manager.create_proxy_file_template()
    
    return {"message": message}

@router.get("/user-stats")
async def get_user_proxy_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de proxies para el usuario actual"""
    
    # Obtener verificaciones del usuario que usaron proxies
    from ..models import CardCheck
    
    user_checks = db.query(CardCheck).filter(
        CardCheck.user_id == current_user.id,
        CardCheck.proxy_used.isnot(None)
    ).all()
    
    # Contar proxies únicos usados
    unique_proxies = set(check.proxy_used for check in user_checks)
    
    # Contar verificaciones por proxy
    proxy_usage = {}
    for check in user_checks:
        if check.proxy_used:
            if check.proxy_used not in proxy_usage:
                proxy_usage[check.proxy_used] = {"total": 0, "success": 0}
            proxy_usage[check.proxy_used]["total"] += 1
            if check.status in ["approved", "declined"]:
                proxy_usage[check.proxy_used]["success"] += 1
    
    return {
        "total_checks_with_proxy": len(user_checks),
        "unique_proxies_used": len(unique_proxies),
        "proxy_usage": proxy_usage
    }
