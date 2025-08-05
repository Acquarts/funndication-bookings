from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la lógica del chatbot existente
from main import (
    cargar_pdfs_directorio, 
    inicializar_base_datos,
    mostrar_todos_los_djs,
    extraer_nombre_dj,
    recopilar_datos_evento,
    finalizar_contratacion,
    verificar_disponibilidad,
    buscar_en_texto
)

# Importar OpenAI handler
try:
    from openai_handler import openai_handler
    OPENAI_ENABLED = openai_handler is not None
except ImportError:
    OPENAI_ENABLED = False
    openai_handler = None

app = FastAPI(title="Funndication DJ Bookings API", version="1.0.0")

# Servir archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos de datos
class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_id: str
    status: str = "active"  # active, completed, error

# Almacenamiento en memoria de sesiones (en producción usar Redis/DB)
sessions: Dict[str, Dict] = {}

# Cargar datos al iniciar
pdfs_data = {}
djs_database = ""
prompt_instrucciones = ""

@app.on_event("startup")
async def startup_event():
    """Inicializar la aplicación al arrancar"""
    global pdfs_data, djs_database, prompt_instrucciones
    
    print("Iniciando Funndication DJ Bookings API...")
    
    # Inicializar base de datos
    inicializar_base_datos()
    print("[OK] Base de datos inicializada")
    
    # Cargar PDFs
    pdfs_data = cargar_pdfs_directorio()
    if len(pdfs_data) < 2:
        print("[WARNING] Se necesitan al menos 2 PDFs")
        return
    
    # Identificar archivos
    for nombre, contenido in pdfs_data.items():
        if "prompt" in nombre.lower():
            prompt_instrucciones = contenido
            print(f"[PROMPT] Instrucciones cargadas desde: {nombre}")
        elif "data" in nombre.lower():
            djs_database = contenido
            print(f"[DATA] Base de datos DJs cargada desde: {nombre}")
    
    print("[OK] Sistema listo para recibir requests")
    
    # Verificar estado de OpenAI
    if OPENAI_ENABLED:
        print("[OK] OpenAI integrado - Conversaciones inteligentes habilitadas")
    else:
        print("[INFO] OpenAI no configurado - Funcionando con lógica de palabras clave")
        print("[INFO] Para habilitar OpenAI, configura OPENAI_API_KEY en .env")

def create_session() -> str:
    """Crear nueva sesión"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "dj_seleccionado": None,
        "datos_evento": {},
        "estado": "inicial"  # inicial, seleccionando_dj, recopilando_datos, finalizado
    }
    return session_id

def get_session(session_id: str) -> Dict:
    """Obtener sesión existente"""
    if session_id not in sessions:
        session_id = create_session()
    return sessions[session_id]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Servir la página principal"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Funndication DJ Bookings</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <script>
            window.location.href = '/static/index.html';
        </script>
        <p>Redirigiendo al chat...</p>
    </body>
    </html>
    """

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """Endpoint principal del chat"""
    try:
        # Obtener o crear sesión
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        message = request.message.strip()
        
        if not message:
            return MessageResponse(
                response="Por favor, dime en que puedo ayudarte.",
                session_id=session_id
            )
        
        # Manejar comando salir
        if message.lower() in ['salir', 'exit', 'quit']:
            if session_id in sessions:
                del sessions[session_id]
            return MessageResponse(
                response="Gracias por tu tiempo y te despido de forma cordial y amigable. Espero que tengas un evento espectacular!",
                session_id=session_id,
                status="completed"
            )
        
        # Procesar mensaje según estado de la sesión
        response = await process_message(session, message)
        
        return MessageResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        return MessageResponse(
            response=f"Lo siento, ocurrió un error: {str(e)}",
            session_id=session_id or create_session(),
            status="error"
        )

async def process_message(session: Dict, message: str) -> str:
    """Procesar mensaje según el estado de la sesión"""
    
    # Si es el primer mensaje o está en estado inicial
    if session["estado"] == "inicial":
        
        # Usar OpenAI si está disponible
        if OPENAI_ENABLED:
            try:
                # Analizar intención con OpenAI
                intent_analysis = openai_handler.analyze_user_intent(message, djs_database)
                
                if intent_analysis["intent"] == "booking" or intent_analysis["confidence"] > 0.7:
                    session["estado"] = "seleccionando_dj"
                    
                    if intent_analysis["entities"]["dj_mentioned"]:
                        # Si mencionó un DJ específico, ir directamente a la selección
                        dj_name = intent_analysis["entities"]["dj_mentioned"]
                        session["dj_seleccionado"] = dj_name
                        session["estado"] = "recopilando_datos"
                        
                        response = f"¡Excelente elección! Has seleccionado a {dj_name}\n"
                        response += openai_handler.extract_dj_info(dj_name, djs_database) + "\n\n"
                        response += "Para cerrar la contratación necesito los siguientes datos obligatorios:\n"
                        response += "+ Localización del evento\n+ Fecha del evento\n+ Duración de la actuación\n"
                        response += "+ Nombre y apellidos\n+ Teléfono\n+ Correo electrónico\n\n"
                        response += "Empecemos con el primer dato.\nLocalización del evento:"
                        return response
                    else:
                        # Mostrar todos los DJs con respuesta inteligente
                        response = openai_handler.generate_response(
                            message, 
                            "Usuario quiere contratar un DJ - mostrar lista completa", 
                            djs_database
                        )
                        response += "\n\n" + "=" * 70 + "\n"
                        response += format_djs_info(djs_database)
                        response += "\n" + "=" * 70 + "\n\n¿Cuál de estos artistas te interesa contratar?"
                        return response
                
                elif intent_analysis["entities"]["dj_mentioned"]:
                    # Pregunta específica sobre un DJ
                    dj_name = intent_analysis["entities"]["dj_mentioned"]
                    return openai_handler.extract_dj_info(dj_name, djs_database)
                
                else:
                    # Respuesta general con OpenAI
                    return openai_handler.generate_response(
                        message, 
                        "Usuario hace pregunta general sobre DJs o servicios", 
                        djs_database
                    )
                    
            except Exception as e:
                print(f"Error con OpenAI: {e}")
                # Fallback al sistema original
        
        # Fallback: Sistema original (sin OpenAI)
        palabras_booking = [
            "contratar", "booking", "book", "contratación", 
            "quiero contratar", "me gustaría contratar", "necesito contratar",
            "busco dj", "busco un dj", "necesito dj", "quiero dj",
            "reservar", "reserva", "evento", "fiesta", "celebración",
            "dj para evento", "dj para fiesta", "contratar dj",
            "precio", "precios", "cuanto cuesta", "tarifas",
            "disponible", "disponibilidad", "fecha"
        ]
        
        if any(palabra in message.lower() for palabra in palabras_booking):
            session["estado"] = "seleccionando_dj"
            
            response = "¡Perfecto! Te muestro todos los DJs que tenemos disponibles con toda su informacion:\n"
            response += "=" * 70 + "\n\n"
            
            # Mostrar todos los DJs
            response += format_djs_info(djs_database)
            
            response += "\n" + "=" * 70
            response += "\n\n¿Cual de estos artistas te interesa contratar?"
            
            return response
        else:
            # Respuestas naturales para mensajes comunes
            return handle_general_message(message, djs_database)
    
    # Si está seleccionando DJ
    elif session["estado"] == "seleccionando_dj":
        # Primero verificar si es una nueva intención de contratación
        palabras_booking = [
            "contratar", "booking", "book", "contratación", 
            "quiero contratar", "me gustaría contratar", "necesito contratar",
            "busco dj", "busco un dj", "necesito dj", "quiero dj",
            "reservar", "reserva", "evento", "fiesta", "celebración",
            "dj para evento", "dj para fiesta", "contratar dj",
            "precio", "precios", "cuanto cuesta", "tarifas",
            "disponible", "disponibilidad", "fecha"
        ]
        
        if any(palabra in message.lower() for palabra in palabras_booking):
            # Usuario quiere contratar, mostrar lista de DJs
            response = "¡Perfecto! Te muestro todos los DJs que tenemos disponibles con toda su informacion:\n"
            response += "=" * 70 + "\n\n"
            
            # Mostrar todos los DJs
            response += format_djs_info(djs_database)
            
            response += "\n" + "=" * 70
            response += "\n\n¿Cual de estos artistas te interesa contratar?"
            
            return response
        else:
            # Intentar extraer nombre de DJ
            dj_seleccionado = extraer_nombre_dj(message)
            if dj_seleccionado != "DJ seleccionado":
                session["dj_seleccionado"] = dj_seleccionado
                session["estado"] = "recopilando_datos"
                
                response = f"¡Excelente eleccion! Has seleccionado a {dj_seleccionado}\n"
                response += "Para cerrar la contratacion necesito los siguientes datos obligatorios:\n"
                response += "+ Localizacion del evento\n"
                response += "+ Fecha del evento\n"
                response += "+ Duracion de la actuacion\n"
                response += "+ Nombre y apellidos\n"
                response += "+ Telefono\n"
                response += "+ Correo electronico\n\n"
                response += "Empecemos con el primer dato.\n"
                response += "Localizacion del evento:"
                
                return response
            else:
                return "No he reconocido ese artista. Por favor, selecciona uno de la lista anterior."
    
    # Si está recopilando datos
    elif session["estado"] == "recopilando_datos":
        resultado = recopilar_datos_evento(session["datos_evento"], message, session["dj_seleccionado"])
        
        if not resultado:
            # Fecha no disponible
            return f"Lo siento, {session['dj_seleccionado']} no está disponible el {message}. Esa fecha ya está ocupada. Por favor, elige otra fecha."
        
        # Si ya tenemos todos los datos
        if len(session["datos_evento"]) == 6:
            session["estado"] = "finalizado"
            
            # Generar respuesta de finalización
            response = finalizar_contratacion_web(session["dj_seleccionado"], session["datos_evento"], djs_database)
            
            return response
        else:
            # Necesitamos más datos
            campos = ["localizacion", "fecha", "duracion", "nombre", "telefono", "email"]
            siguiente_campo = campos[len(session["datos_evento"])]
            nombres_campos = {
                "localizacion": "Localizacion del evento",
                "fecha": "Fecha del evento", 
                "duracion": "Duracion de la actuacion",
                "nombre": "Nombre y apellidos",
                "telefono": "Telefono",
                "email": "Correo electronico"
            }
            
            return f"[OK] {campos[len(session['datos_evento'])-1].capitalize()}: {message}\n\nAhora necesito: {nombres_campos[siguiente_campo]}"
    
    # Estado por defecto
    return "¿En que puedo ayudarte?"

def format_djs_info(database: str) -> str:
    """Formatear información de DJs para mostrar en web"""
    lineas = database.split('\n')
    dj_info = ""
    resultado = ""
    
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith("NOMBRE:"):
            if dj_info:
                resultado += dj_info + "\n" + "-" * 50 + "\n\n"
            dj_info = linea + "\n"
        elif linea and not linea.startswith("CHATBOT") and not linea.startswith("ARTISTAS:") and not linea.startswith("INGRESOS") and not linea.startswith("PRESS"):
            dj_info += linea + "\n"
    
    if dj_info:
        resultado += dj_info
    
    return resultado

def handle_general_message(message: str, database: str) -> str:
    """Maneja mensajes generales con respuestas naturales"""
    message_lower = message.lower().strip()
    
    # Saludos
    saludos = ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches", "hey", "que tal"]
    if any(saludo in message_lower for saludo in saludos):
        return ("¡Hola! Soy tu manager de DJs de Funndication Bookings. 🎵\n\n"
                "Estoy aquí para ayudarte a contratar el DJ perfecto para tu evento.\n\n"
                "Puedes decirme:\n"
                "• 'Quiero contratar un DJ'\n"
                "• 'Precios de DJs'\n"
                "• 'Cuánto cuesta [nombre del DJ]'\n"
                "• 'Disponibilidad para [fecha]'\n\n"
                "¿En qué puedo ayudarte hoy?")
    
    # Despedidas
    despedidas = ["adiós", "adios", "hasta luego", "bye", "chao", "nos vemos"]
    if any(despedida in message_lower for despedida in despedidas):
        return ("¡Hasta luego! Ha sido un placer ayudarte.\n\n"
                "Si necesitas contratar algún DJ en el futuro, ya sabes dónde encontrarme. 🎧\n\n"
                "¡Que tengas un día espectacular!")
    
    # Agradecimientos
    gracias = ["gracias", "thank you", "thanks", "muchas gracias"]
    if any(palabra in message_lower for palabra in gracias):
        return ("¡De nada! Es un placer ayudarte con tu booking. 😊\n\n"
                "¿Hay algo más en lo que pueda asistirte?")
    
    # Preguntas sobre el servicio
    if any(palabra in message_lower for palabra in ["que haces", "qué haces", "quien eres", "quién eres", "servicio"]):
        return ("Soy el manager de DJs más especializado de Funndication Bookings. 🎵\n\n"
                "Me encargo de:\n"
                "✅ Ayudarte a encontrar el DJ perfecto\n"
                "✅ Calcular precios exactos según tu evento\n"
                "✅ Verificar disponibilidad de fechas\n"
                "✅ Gestionar toda la contratación\n\n"
                "Tenemos 5 increíbles DJs especializados en Break Beat.\n\n"
                "¿Te gustaría ver nuestros artistas disponibles?")
    
    # Preguntas sobre géneros musicales
    if any(palabra in message_lower for palabra in ["música", "genero", "género", "estilo", "break beat", "breakbeat"]):
        return ("¡Excelente pregunta! Nuestros DJs se especializan en Break Beat. 🎵\n\n"
                "Es un género electrónico con ritmos únicos y energia increíble, "
                "perfecto para cualquier tipo de evento.\n\n"
                "Todos nuestros artistas dominan este estilo a la perfección:\n"
                "• The Brainkiller\n"
                "• Jose Rodriguez\n"
                "• Tortu\n"
                "• V. Aparicio\n"
                "• Wardian\n\n"
                "¿Te gustaría conocer más sobre alguno en particular?")
    
    # Preguntas sobre precios generales
    if any(palabra in message_lower for palabra in ["caro", "barato", "económico", "presupuesto", "cuanto"]):
        return ("Te explico nuestros rangos de precios: 💰\n\n"
                "🎵 **Opciones más económicas:**\n"
                "• V. Aparicio: desde 600€\n"
                "• Wardian: desde 600€\n\n"
                "🎵 **Rango medio:**\n"
                "• Jose Rodriguez: desde 1.000€\n"
                "• Tortu: desde 1.200€\n\n"
                "🎵 **Premium:**\n"
                "• The Brainkiller: desde 1.600€\n\n"
                "Los precios incluyen 1 hora base, +300€ por hora adicional.\n"
                "¿Te interesa alguno en particular?")
    
    # Si no reconoce nada, buscar en la base de datos
    informacion = buscar_en_texto(database, message)
    if informacion and "No encontré información específica" not in informacion:
        return f"Basándome en nuestra base de datos: {informacion}"
    
    # Respuesta por defecto más natural
    return ("No estoy seguro de entender exactamente qué necesitas. 🤔\n\n"
            "Te puedo ayudar con:\n"
            "• Contratar DJs para tu evento\n"
            "• Consultar precios y disponibilidad\n"
            "• Información sobre nuestros artistas\n\n"
            "¿Podrías decirme qué tipo de ayuda necesitas?")

def finalizar_contratacion_web(dj: str, datos: Dict, database: str) -> str:
    """Versión web de finalizar_contratacion que retorna string"""
    from main import guardar_contratacion
    
    response = f"¡Excelente! He recogido todos los datos para contratar a {dj}\n"
    response += "=" * 50 + "\n"
    response += "RESUMEN DE LA CONTRATACION:\n"
    response += f"DJ: {dj}\n"
    response += f"Localizacion: {datos['localizacion']}\n"
    response += f"Fecha: {datos['fecha']}\n"
    response += f"Duracion: {datos['duracion']}\n"
    response += f"Cliente: {datos['nombre']}\n"
    response += f"Telefono: {datos['telefono']}\n"
    response += f"Email: {datos['email']}\n"
    response += "=" * 50 + "\n\n"
    
    # Calcular precio (usando la lógica existente)
    response += "DESGLOSE DEL PRECIO:\n\n"
    
    # Precios exactos del PDF
    precios_djs = {
        "The Brainkiller": {"base": 1600, "fuera_malaga": 1800, "fuera_espana": 2500},
        "Jose Rodriguez": {"base": 1000, "fuera_malaga": 1200, "fuera_espana": 1900},
        "Tortu": {"base": 1200, "fuera_malaga": 1400, "fuera_espana": 2100},
        "V. Aparicio": {"base": 600, "fuera_malaga": 800, "fuera_espana": 1500},
        "Wardian": {"base": 600, "fuera_malaga": 800, "fuera_espana": 1500}
    }
    
    precios_dj = precios_djs.get(dj, precios_djs["V. Aparicio"])
    localizacion = datos['localizacion'].lower()
    
    if "málaga" in localizacion or "malaga" in localizacion:
        precio_base = precios_dj["base"]
        response += f"Caché base {dj} (Málaga): {precio_base}€\n"
    elif any(pais in localizacion for pais in ["francia", "portugal", "italia", "alemania", "reino unido", "uk", "france", "germany", "italy"]) or "fuera de españa" in localizacion:
        precio_base = precios_dj["fuera_espana"]
        response += f"Caché {dj} fuera de España: {precio_base}€\n"
        response += "(No incluido hotel, desplazamiento y comida)\n"
    else:
        precio_base = precios_dj["fuera_malaga"]
        response += f"Caché {dj} fuera de Málaga: {precio_base}€\n"
        response += "(No incluido hotel, desplazamiento y comida)\n"
    
    # Calcular horas adicionales
    import re
    duracion_texto = datos['duracion'].lower()
    horas = 1
    
    if 'hora' in duracion_texto:
        numeros = re.findall(r'\d+', duracion_texto)
        if numeros:
            horas = int(numeros[0])
    
    precio_horas_extra = 0
    if horas > 1:
        horas_extra = horas - 1
        precio_horas_extra = horas_extra * 300
        response += f"Horas adicionales ({horas_extra}h x 300€): +{precio_horas_extra}€\n"
    
    precio_total = precio_base + precio_horas_extra
    
    response += "-" * 40 + "\n"
    response += f"TOTAL: {precio_total}€\n"
    response += "-" * 40 + "\n\n"
    
    response += "Para cerrar la contratacion debe hacer el ingreso a la cuenta:\n"
    response += "NUMERO DE CUENTA: 78979566700116362718\n\n"
    response += "Recibira un correo de confirmacion cuando el ingreso sea recibido.\n\n"
    response += "Tambien puede descargar los press kits desde:\n"
    response += "https://www.funndarkbookings/presskits.com\n\n"
    
    # Guardar en base de datos
    guardar_contratacion(dj, datos, precio_total)
    response += "[OK] Contratación guardada correctamente en el sistema\n\n"
    
    response += f"¡Gracias por confiar en nosotros para tu evento con {dj}!\n"
    response += "¡Que tengas un espectaculo increible!"
    
    return response

@app.get("/health")
async def health_check():
    """Endpoint de salud para Railway"""
    return {"status": "healthy", "message": "Funndication DJ Bookings API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)