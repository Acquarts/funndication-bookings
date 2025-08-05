import os
import openai
from dotenv import load_dotenv
from typing import Dict, Optional
import json

# Cargar variables de entorno
load_dotenv()

class OpenAIHandler:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
    def get_system_prompt(self, djs_database: str) -> str:
        """Genera el prompt del sistema con información de los DJs"""
        return f"""Eres el mejor manager de DJs de Funndication DJ Bookings, especializado en contratación de artistas.

INFORMACIÓN DE DJS DISPONIBLES:
{djs_database}

PRECIOS Y REGLAS (EXACTAS):
- The Brainkiller: 1.600€ base (Málaga), 1.800€ fuera Málaga, 2.500€ fuera España
- Jose Rodriguez: 1.000€ base (Málaga), 1.200€ fuera Málaga, 1.900€ fuera España  
- Tortu: 1.200€ base (Málaga), 1.400€ fuera Málaga, 2.100€ fuera España
- V. Aparicio: 600€ base (Málaga), 800€ fuera Málaga, 1.500€ fuera España
- Wardian: 600€ base (Málaga), 800€ fuera Málaga, 1.500€ fuera España

REGLAS IMPORTANTES:
- Caché base = 1 hora de trabajo
- +300€ por cada hora adicional
- Fuera de Málaga/España no incluye hotel, desplazamiento y comida
- Todos los DJs están disponibles cualquier día del año
- Número de cuenta: 78979566700116362718
- Press kits: https://www.funndarkbookings/presskits.com

TU PERSONALIDAD:
- Profesional pero amigable
- Entusiasta sobre la música electrónica
- Experto en Break Beat
- Ayudas a encontrar el DJ perfecto para cada evento

TAREAS:
1. Identificar intención de contratación (contratar, booking, reservar, precio, etc.)
2. Recomendar DJs según presupuesto/evento
3. Explicar precios claramente
4. Guiar el proceso de contratación paso a paso
5. Responder preguntas sobre los artistas

RESPONDE SIEMPRE EN ESPAÑOL y mantén un tono profesional pero cercano."""

    def analyze_user_intent(self, message: str, djs_database: str) -> Dict:
        """Analiza la intención del usuario usando OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"""Analiza la intención del usuario en este mensaje sobre contratación de DJs.

DJS DISPONIBLES: {djs_database}

Devuelve un JSON con:
{{
    "intent": "booking|info|greeting|other",
    "confidence": 0.0-1.0,
    "entities": {{
        "dj_mentioned": "nombre_dj o null",
        "event_type": "tipo_evento o null",
        "location": "ubicación o null",
        "budget_mentioned": true/false
    }},
    "suggested_response_type": "show_djs|provide_info|ask_clarification|greeting"
}}

Ejemplos:
- "quiero contratar un dj" -> intent: "booking", suggested_response_type: "show_djs"
- "cuanto cuesta The Brainkiller" -> intent: "info", entities: {{"dj_mentioned": "The Brainkiller"}}, suggested_response_type: "provide_info"
- "hola" -> intent: "greeting", suggested_response_type: "greeting"
"""
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error analyzing intent: {e}")
            # Fallback a análisis simple
            return self._simple_intent_analysis(message)
    
    def _simple_intent_analysis(self, message: str) -> Dict:
        """Análisis de intención simple como fallback"""
        message_lower = message.lower()
        
        booking_words = ["contratar", "booking", "book", "reservar", "precio", "cuanto", "tarifa"]
        dj_names = ["brainkiller", "jose", "rodriguez", "tortu", "aparicio", "wardian"]
        
        intent = "other"
        confidence = 0.5
        suggested_response_type = "ask_clarification"
        
        if any(word in message_lower for word in booking_words):
            intent = "booking"
            confidence = 0.8
            suggested_response_type = "show_djs"
        
        dj_mentioned = None
        for dj in dj_names:
            if dj in message_lower:
                if "brainkiller" in message_lower:
                    dj_mentioned = "The Brainkiller"
                elif "jose" in message_lower or "rodriguez" in message_lower:
                    dj_mentioned = "Jose Rodriguez"
                elif "tortu" in message_lower:
                    dj_mentioned = "Tortu"
                elif "aparicio" in message_lower:
                    dj_mentioned = "V. Aparicio"
                elif "wardian" in message_lower:
                    dj_mentioned = "Wardian"
                break
        
        if dj_mentioned:
            intent = "info"
            suggested_response_type = "provide_info"
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {
                "dj_mentioned": dj_mentioned,
                "event_type": None,
                "location": None,
                "budget_mentioned": "precio" in message_lower or "cuanto" in message_lower
            },
            "suggested_response_type": suggested_response_type
        }
    
    def generate_response(self, message: str, context: str, djs_database: str) -> str:
        """Genera una respuesta contextual usando OpenAI"""
        try:
            system_prompt = self.get_system_prompt(djs_database)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contexto: {context}\n\nUsuario dice: {message}"}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Lo siento, tengo problemas técnicos. ¿Podrías repetir tu pregunta?"
    
    def extract_dj_info(self, dj_name: str, djs_database: str) -> str:
        """Extrae información específica de un DJ"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Extrae y formatea la información específica sobre {dj_name} de esta base de datos:

{djs_database}

Presenta la información de forma clara y atractiva, incluyendo:
- Nombre y procedencia
- Estilo musical
- Precios completos (base, fuera Málaga, fuera España)
- Regla de horas adicionales
- Enlaces de redes sociales
- Disponibilidad

Mantén un tono profesional pero entusiasta."""
                    },
                    {"role": "user", "content": f"Dame información detallada sobre {dj_name}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error extracting DJ info: {e}")
            # Fallback a búsqueda simple en texto
            lines = djs_database.split('\n')
            dj_info = []
            capture = False
            
            for line in lines:
                if f"NOMBRE: {dj_name}" in line:
                    capture = True
                elif line.startswith("NOMBRE:") and capture:
                    break
                elif line.startswith("___") and capture:
                    break
                
                if capture:
                    dj_info.append(line.strip())
            
            return '\n'.join(dj_info) if dj_info else f"No encontré información específica sobre {dj_name}"

# Instancia global
openai_handler = OpenAIHandler() if os.getenv("OPENAI_API_KEY") else None