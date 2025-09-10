from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Script, ScriptExecution
from ..schemas import ScriptCreate, ScriptUpdate, Script as ScriptSchema, ScriptExecution as ScriptExecutionSchema
from ..auth import get_current_active_user, get_current_admin_user
from ..script_executor import ScriptExecutor

router = APIRouter(prefix="/scripts", tags=["scripts"])

@router.post("/", response_model=ScriptSchema)
async def create_script(
    script: ScriptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo script"""
    
    if script.language.lower() not in ["python", "php"]:
        raise HTTPException(
            status_code=400,
            detail="Lenguaje no soportado. Solo se permiten Python y PHP"
        )
    
    db_script = Script(
        name=script.name,
        content=script.content,
        language=script.language,
        user_id=current_user.id
    )
    
    db.add(db_script)
    db.commit()
    db.refresh(db_script)
    
    return db_script

@router.get("/", response_model=List[ScriptSchema])
async def get_user_scripts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener scripts del usuario actual"""
    
    scripts = db.query(Script).filter(
        Script.user_id == current_user.id,
        Script.is_active == True
    ).all()
    
    return scripts

@router.get("/all", response_model=List[ScriptSchema])
async def get_all_scripts(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los scripts (solo admin)"""
    
    scripts = db.query(Script).filter(Script.is_active == True).all()
    return scripts

@router.get("/{script_id}", response_model=ScriptSchema)
async def get_script(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener script específico"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.is_active == True
    ).first()
    
    if not script:
        raise HTTPException(
            status_code=404,
            detail="Script no encontrado"
        )
    
    # Verificar que el usuario sea el propietario o admin
    if script.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver este script"
        )
    
    return script

@router.put("/{script_id}", response_model=ScriptSchema)
async def update_script(
    script_id: int,
    script_update: ScriptUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.is_active == True
    ).first()
    
    if not script:
        raise HTTPException(
            status_code=404,
            detail="Script no encontrado"
        )
    
    # Verificar que el usuario sea el propietario o admin
    if script.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para editar este script"
        )
    
    # Actualizar campos
    if script_update.name is not None:
        script.name = script_update.name
    if script_update.content is not None:
        script.content = script_update.content
    if script_update.language is not None:
        if script_update.language.lower() not in ["python", "php"]:
            raise HTTPException(
                status_code=400,
                detail="Lenguaje no soportado. Solo se permiten Python y PHP"
            )
        script.language = script_update.language
    
    db.commit()
    db.refresh(script)
    
    return script

@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar script (soft delete)"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.is_active == True
    ).first()
    
    if not script:
        raise HTTPException(
            status_code=404,
            detail="Script no encontrado"
        )
    
    # Verificar que el usuario sea el propietario o admin
    if script.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar este script"
        )
    
    script.is_active = False
    db.commit()
    
    return {"message": "Script eliminado exitosamente"}

@router.post("/{script_id}/execute", response_model=ScriptExecutionSchema)
async def execute_script(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ejecutar script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.is_active == True
    ).first()
    
    if not script:
        raise HTTPException(
            status_code=404,
            detail="Script no encontrado"
        )
    
    # Verificar que el usuario sea el propietario o admin
    if script.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ejecutar este script"
        )
    
    # Ejecutar script
    executor = ScriptExecutor(db)
    execution = await executor.execute_script(script)
    
    return execution

@router.get("/{script_id}/executions", response_model=List[ScriptExecutionSchema])
async def get_script_executions(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de ejecuciones de un script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.is_active == True
    ).first()
    
    if not script:
        raise HTTPException(
            status_code=404,
            detail="Script no encontrado"
        )
    
    # Verificar que el usuario sea el propietario o admin
    if script.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver las ejecuciones de este script"
        )
    
    executions = db.query(ScriptExecution).filter(
        ScriptExecution.script_id == script_id
    ).order_by(ScriptExecution.started_at.desc()).all()
    
    return executions
