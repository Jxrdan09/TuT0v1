import os
import random
import asyncio
import aiohttp
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from .models import Proxy
from datetime import datetime

class ProxyManager:
    def __init__(self, db: Session):
        self.db = db
        self.proxy_file_path = "proxies.txt"
    
    def load_proxies_from_file(self) -> List[str]:
        """Cargar proxies desde archivo TXT"""
        proxies = []
        
        if not os.path.exists(self.proxy_file_path):
            return proxies
        
        try:
            with open(self.proxy_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Ignorar líneas vacías y comentarios
                        proxies.append(line)
        except Exception as e:
            print(f"Error cargando proxies desde archivo: {e}")
        
        return proxies
    
    def save_proxies_to_database(self, proxies: List[str], proxy_type: str = "http") -> int:
        """Guardar proxies en la base de datos"""
        added_count = 0
        
        for proxy_string in proxies:
            # Verificar si el proxy ya existe
            existing_proxy = self.db.query(Proxy).filter(
                Proxy.proxy_string == proxy_string
            ).first()
            
            if not existing_proxy:
                proxy = Proxy(
                    proxy_string=proxy_string,
                    proxy_type=proxy_type
                )
                self.db.add(proxy)
                added_count += 1
        
        self.db.commit()
        return added_count
    
    def load_proxies_from_file_to_db(self, proxy_type: str = "http") -> Dict:
        """Cargar proxies desde archivo TXT y guardarlos en la base de datos"""
        proxies = self.load_proxies_from_file()
        
        if not proxies:
            return {
                "success": False,
                "message": "No se encontraron proxies en el archivo",
                "added": 0,
                "total": 0
            }
        
        added_count = self.save_proxies_to_database(proxies, proxy_type)
        
        return {
            "success": True,
            "message": f"Proxies cargados exitosamente",
            "added": added_count,
            "total": len(proxies)
        }
    
    def get_random_proxy(self) -> Optional[Proxy]:
        """Obtener un proxy aleatorio activo"""
        active_proxies = self.db.query(Proxy).filter(
            Proxy.is_active == True
        ).all()
        
        if not active_proxies:
            return None
        
        return random.choice(active_proxies)
    
    def get_proxy_for_request(self) -> Optional[Dict]:
        """Obtener un proxy formateado para usar en requests"""
        # Primero intentar obtener un proxy rotativo
        rotating_proxy = self.get_rotating_proxy()
        if rotating_proxy:
            return rotating_proxy
        
        # Si no hay proxies rotativos, usar un proxy normal
        proxy = self.get_random_proxy()
        
        if not proxy:
            return None
        
        # Actualizar último uso solo para proxies no rotativos
        proxy.last_used = datetime.utcnow()
        self.db.commit()
        
        return self.format_proxy_for_requests(proxy)
    
    def format_proxy_for_requests(self, proxy: Proxy) -> Dict:
        """Formatear proxy para usar con aiohttp/requests"""
        parts = proxy.proxy_string.split(':')
        
        if len(parts) == 2:
            # Formato: ip:port
            ip, port = parts
            proxy_url = f"{proxy.proxy_type}://{ip}:{port}"
            return {
                "proxy": proxy_url,
                "proxy_string": proxy.proxy_string,
                "proxy_id": proxy.id
            }
        elif len(parts) == 4:
            # Formato: ip:port:user:pass
            ip, port, user, password = parts
            proxy_url = f"{proxy.proxy_type}://{user}:{password}@{ip}:{port}"
            return {
                "proxy": proxy_url,
                "proxy_string": proxy.proxy_string,
                "proxy_id": proxy.id
            }
        else:
            return None
    
    def get_rotating_proxy(self) -> Optional[Dict]:
        """Obtener un proxy rotativo (para proxies que cambian IP automáticamente)"""
        # Buscar proxies que contengan indicadores de rotación
        rotating_proxies = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.proxy_string.like('%proxy-cheap%')
        ).all()
        
        if rotating_proxies:
            # Para proxies rotativos, no actualizar last_used para evitar sobrecarga
            proxy = random.choice(rotating_proxies)
            return self.format_proxy_for_requests(proxy)
        
        return None
    
    async def test_proxy(self, proxy: Proxy, timeout: int = 10) -> bool:
        """Probar si un proxy funciona"""
        formatted_proxy = self.format_proxy_for_requests(proxy)
        
        if not formatted_proxy:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=formatted_proxy['proxy'],
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        return True
        except Exception as e:
            print(f"Error probando proxy {proxy.proxy_string}: {e}")
        
        return False
    
    async def test_all_proxies(self) -> Dict:
        """Probar todos los proxies activos"""
        active_proxies = self.db.query(Proxy).filter(
            Proxy.is_active == True
        ).all()
        
        if not active_proxies:
            return {
                "success": False,
                "message": "No hay proxies activos para probar",
                "tested": 0,
                "working": 0,
                "failed": 0
            }
        
        working_count = 0
        failed_count = 0
        
        # Probar proxies en lotes para no sobrecargar
        batch_size = 10
        for i in range(0, len(active_proxies), batch_size):
            batch = active_proxies[i:i + batch_size]
            
            # Crear tareas para probar el lote
            tasks = [self.test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for proxy, result in zip(batch, results):
                if isinstance(result, Exception) or not result:
                    proxy.failure_count += 1
                    failed_count += 1
                else:
                    proxy.success_count += 1
                    working_count += 1
        
        self.db.commit()
        
        return {
            "success": True,
            "message": "Prueba de proxies completada",
            "tested": len(active_proxies),
            "working": working_count,
            "failed": failed_count
        }
    
    def update_proxy_stats(self, proxy_id: int, success: bool):
        """Actualizar estadísticas de un proxy"""
        proxy = self.db.query(Proxy).filter(Proxy.id == proxy_id).first()
        
        if proxy:
            if success:
                proxy.success_count += 1
            else:
                proxy.failure_count += 1
            
            proxy.last_used = datetime.utcnow()
            self.db.commit()
    
    def get_proxy_stats(self) -> Dict:
        """Obtener estadísticas de proxies"""
        total_proxies = self.db.query(Proxy).count()
        active_proxies = self.db.query(Proxy).filter(Proxy.is_active == True).count()
        
        # Obtener proxies con mejor tasa de éxito
        best_proxies = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.success_count > 0
        ).order_by(
            (Proxy.success_count / (Proxy.success_count + Proxy.failure_count)).desc()
        ).limit(5).all()
        
        return {
            "total_proxies": total_proxies,
            "active_proxies": active_proxies,
            "inactive_proxies": total_proxies - active_proxies,
            "best_proxies": [
                {
                    "id": p.id,
                    "proxy_string": p.proxy_string,
                    "success_rate": p.success_rate,
                    "success_count": p.success_count,
                    "failure_count": p.failure_count
                }
                for p in best_proxies
            ]
        }
    
    def create_proxy_file_template(self):
        """Crear archivo de plantilla para proxies"""
        template_content = """# Archivo de Proxies
# Formato: ip:port o ip:port:usuario:contraseña
# Un proxy por línea
# Las líneas que empiecen con # son comentarios

# Ejemplos:
# 192.168.1.1:8080
# 192.168.1.2:8080:usuario:contraseña
# 10.0.0.1:3128

# Agrega tus proxies aquí:
"""
        
        with open(self.proxy_file_path, 'w', encoding='utf-8') as file:
            file.write(template_content)
        
        return f"Archivo de plantilla creado: {self.proxy_file_path}"
