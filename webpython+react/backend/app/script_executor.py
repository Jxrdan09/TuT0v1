import subprocess
import tempfile
import os
import asyncio
from typing import Dict, Any
from .models import Script, ScriptExecution
from sqlalchemy.orm import Session

class ScriptExecutor:
    def __init__(self, db: Session):
        self.db = db
    
    async def execute_script(self, script: Script) -> ScriptExecution:
        """Ejecuta un script Python o PHP de forma asíncrona"""
        
        # Crear registro de ejecución
        execution = ScriptExecution(
            script_id=script.id,
            status="running"
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        try:
            if script.language.lower() == "python":
                result = await self._execute_python_script(script.content)
            elif script.language.lower() == "php":
                result = await self._execute_php_script(script.content)
            else:
                raise ValueError(f"Lenguaje no soportado: {script.language}")
            
            # Actualizar ejecución con resultado
            execution.status = "completed"
            execution.output = result.get("output", "")
            execution.error = result.get("error", "")
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
        
        self.db.commit()
        return execution
    
    async def _execute_python_script(self, code: str) -> Dict[str, Any]:
        """Ejecuta código Python de forma segura"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Ejecutar con timeout de 30 segundos
            process = await asyncio.create_subprocess_exec(
                'python3', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            
            return {
                "output": stdout.decode('utf-8'),
                "error": stderr.decode('utf-8') if stderr else None
            }
            
        except asyncio.TimeoutError:
            return {"error": "El script excedió el tiempo límite de 30 segundos"}
        except Exception as e:
            return {"error": f"Error ejecutando script: {str(e)}"}
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    async def _execute_php_script(self, code: str) -> Dict[str, Any]:
        """Ejecuta código PHP de forma segura"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Ejecutar con timeout de 30 segundos
            process = await asyncio.create_subprocess_exec(
                'php', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            
            return {
                "output": stdout.decode('utf-8'),
                "error": stderr.decode('utf-8') if stderr else None
            }
            
        except asyncio.TimeoutError:
            return {"error": "El script excedió el tiempo límite de 30 segundos"}
        except Exception as e:
            return {"error": f"Error ejecutando script: {str(e)}"}
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
