from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import random
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..schemas import User
from datetime import datetime

router = APIRouter(prefix="/api/gates", tags=["gates"])

# Simulación de datos de gates
GATES_DATA = {
    "IRIS": {
        "id": "IRIS",
        "name": "IRIS",
        "type": "auth",
        "status": {"live": 2, "dead": 1},
        "config": {
            "endpoint": "/api/gates/iris",
            "timeout": 30000,
            "retries": 3
        }
    },
    "KAIROS": {
        "id": "KAIROS",
        "name": "KAIROS",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/kairos",
            "timeout": 30000,
            "retries": 3
        }
    },
    "DIONE": {
        "id": "DIONE",
        "name": "DIONE",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/dione",
            "timeout": 30000,
            "retries": 3
        }
    },
    "HEBE": {
        "id": "HEBE",
        "name": "HEBE",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/hebe",
            "timeout": 30000,
            "retries": 3
        }
    },
    "PAYPAL": {
        "id": "PAYPAL",
        "name": "PAYPAL",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/paypal",
            "timeout": 30000,
            "retries": 3
        }
    },
    "LUXURY": {
        "id": "LUXURY",
        "name": "LUXURY",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/luxury",
            "timeout": 30000,
            "retries": 3
        }
    },
    "HERMES": {
        "id": "HERMES",
        "name": "HERMES",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/hermes",
            "timeout": 30000,
            "retries": 3
        }
    },
    "CEO": {
        "id": "CEO",
        "name": "CEO",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/ceo",
            "timeout": 30000,
            "retries": 3
        }
    },
    "TEMIS": {
        "id": "TEMIS",
        "name": "TEMIS",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/temis",
            "timeout": 30000,
            "retries": 3
        }
    },
    "CRIO": {
        "id": "CRIO",
        "name": "CRIO",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/crio",
            "timeout": 30000,
            "retries": 3
        }
    },
    "ZEUS": {
        "id": "ZEUS",
        "name": "ZEUS",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/zeus",
            "timeout": 30000,
            "retries": 3
        }
    },
    "GRANO": {
        "id": "GRANO",
        "name": "GRANO",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/grano",
            "timeout": 30000,
            "retries": 3
        }
    },
    "HADES": {
        "id": "HADES",
        "name": "HADES",
        "type": "auth",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/hades",
            "timeout": 30000,
            "retries": 3
        }
    },
    "CHARGE1": {
        "id": "CHARGE1",
        "name": "CHARGE 1",
        "type": "charge",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/charge1",
            "timeout": 30000,
            "retries": 3
        }
    },
    "CHARGE2": {
        "id": "CHARGE2",
        "name": "CHARGE 2",
        "type": "charge",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/charge2",
            "timeout": 30000,
            "retries": 3
        }
    },
    "CHARGE3": {
        "id": "CHARGE3",
        "name": "CHARGE 3",
        "type": "charge",
        "status": {"live": 0, "dead": 0},
        "config": {
            "endpoint": "/api/gates/charge3",
            "timeout": 30000,
            "retries": 3
        }
    }
}

@router.get("/")
async def get_all_gates(current_user: User = Depends(get_current_user)):
    """Obtener todos los gates disponibles"""
    # Verificar suscripción
    if getattr(current_user, 'subscription_expires_at', None) and current_user.subscription_expires_at < datetime.utcnow():
        raise HTTPException(status_code=402, detail="Suscripción expirada")
    return {
        "gates": GATES_DATA,
        "global_stats": {
            "lives_today": 347,
            "total_lives": 3738178
        }
    }

@router.get("/{gate_id}")
async def get_gate(gate_id: str, current_user: User = Depends(get_current_user)):
    """Obtener información de un gate específico"""
    if getattr(current_user, 'subscription_expires_at', None) and current_user.subscription_expires_at < datetime.utcnow():
        raise HTTPException(status_code=402, detail="Suscripción expirada")
    if gate_id not in GATES_DATA:
        raise HTTPException(status_code=404, detail="Gate no encontrado")
    
    return GATES_DATA[gate_id]

@router.post("/{gate_id}/check")
async def check_gate(
    gate_id: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Verificar datos usando un gate específico"""
    if getattr(current_user, 'subscription_expires_at', None) and current_user.subscription_expires_at < datetime.utcnow():
        raise HTTPException(status_code=402, detail="Suscripción expirada")
    if gate_id not in GATES_DATA:
        raise HTTPException(status_code=404, detail="Gate no encontrado")
    
    # Simular verificación
    await asyncio.sleep(2)  # Simular tiempo de procesamiento
    
    # Generar resultados aleatorios
    results = {
        "liveCVV": random.randint(0, 3),
        "liveCNN": random.randint(0, 2),
        "insufficientFunds": random.randint(0, 2),
        "dead": random.randint(0, 5),
        "incorrect": random.randint(0, 2),
        "authenticationRequired": random.randint(0, 1)
    }
    
    # Actualizar estadísticas del gate
    total_live = results["liveCVV"] + results["liveCNN"]
    total_dead = results["dead"] + results["incorrect"] + results["authenticationRequired"]
    
    GATES_DATA[gate_id]["status"]["live"] += total_live
    GATES_DATA[gate_id]["status"]["dead"] += total_dead
    
    return {
        "gate_id": gate_id,
        "results": results,
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.id
    }

@router.get("/{gate_id}/status")
async def get_gate_status(gate_id: str, current_user: User = Depends(get_current_user)):
    """Obtener el estado actual de un gate"""
    if gate_id not in GATES_DATA:
        raise HTTPException(status_code=404, detail="Gate no encontrado")
    
    return {
        "gate_id": gate_id,
        "status": GATES_DATA[gate_id]["status"],
        "last_updated": datetime.now().isoformat()
    }

@router.post("/{gate_id}/reset")
async def reset_gate_status(gate_id: str, current_user: User = Depends(get_current_user)):
    """Resetear el estado de un gate"""
    if gate_id not in GATES_DATA:
        raise HTTPException(status_code=404, detail="Gate no encontrado")
    
    GATES_DATA[gate_id]["status"] = {"live": 0, "dead": 0}
    
    return {
        "message": f"Estado del gate {gate_id} reseteado",
        "status": GATES_DATA[gate_id]["status"]
    }

@router.get("/stats/global")
async def get_global_stats(current_user: User = Depends(get_current_user)):
    """Obtener estadísticas globales"""
    total_live = sum(gate["status"]["live"] for gate in GATES_DATA.values())
    total_dead = sum(gate["status"]["dead"] for gate in GATES_DATA.values())
    
    return {
        "lives_today": 347,
        "total_lives": 3738178,
        "gates_total_live": total_live,
        "gates_total_dead": total_dead,
        "active_gates": len([g for g in GATES_DATA.values() if g["status"]["live"] > 0 or g["status"]["dead"] > 0])
    }
