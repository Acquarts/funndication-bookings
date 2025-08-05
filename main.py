import PyPDF2
import os
import glob
import sqlite3
import datetime
import re

def leer_archivo(nombre_archivo):
    """Lee un archivo de texto o PDF"""
    if nombre_archivo.lower().endswith('.pdf'):
        try:
            with open(nombre_archivo, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                texto = ""
                for page in reader.pages:
                    texto += page.extract_text() or ""
                return texto if texto else "No se pudo extraer texto del PDF."
        except Exception as e:
            return f"Error al leer el PDF: {e}"
    else:
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error al leer el archivo de texto: {e}"
        
# ... tu función leer_archivo() arriba ...

def buscar_en_texto(texto, pregunta):
    """Busca información relevante en el texto para responder una pregunta"""
    if not texto or len(texto.strip()) == 0:
        return "No hay texto para analizar."
    
    # Convertir a minúsculas para búsqueda
    texto_lower = texto.lower()
    pregunta_lower = pregunta.lower()
    
    # Palabras clave de la pregunta
    palabras_pregunta = pregunta_lower.split()
    palabras_relevantes = [p for p in palabras_pregunta if len(p) > 2]
    
    # Dividir texto en oraciones
    oraciones = texto.replace('\n', ' ').split('.')
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 10]
    
    # Buscar oraciones que contengan palabras clave
    oraciones_relevantes = []
    for oracion in oraciones:
        oracion_lower = oracion.lower()
        coincidencias = sum(1 for palabra in palabras_relevantes if palabra in oracion_lower)
        if coincidencias > 0:
            oraciones_relevantes.append((oracion, coincidencias))
    
    if not oraciones_relevantes:
        return "No encontré información específica sobre esa pregunta en el PDF."
    
    # Ordenar por relevancia y tomar las mejores
    oraciones_relevantes.sort(key=lambda x: x[1], reverse=True)
    mejores_oraciones = [o[0] for o in oraciones_relevantes[:3]]
    
    return '. '.join(mejores_oraciones) + '.'

def preguntar_pdf(nombre_archivo):
    """Permite hacer preguntas sobre el contenido de un PDF"""
    contenido = leer_archivo(nombre_archivo)
    if contenido.startswith("Error"):
        return contenido, None
    
    print(f"\nContenido del PDF '{nombre_archivo}' cargado correctamente.")
    print("Puedes hacer preguntas sobre su contenido. Escribe 'salir' para terminar.\n")
    
    while True:
        pregunta = input("¿Qué quieres saber sobre el PDF?: ").strip()
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("¡Hasta luego!")
            break
            
        if not pregunta:
            print("Por favor escribe una pregunta.")
            continue
            
        respuesta = buscar_en_texto(contenido, pregunta)
        print(f"\nRespuesta: {respuesta}\n")
    
    return "Sesión de preguntas terminada.", None

def cargar_pdfs_directorio():
    """Carga automáticamente todos los PDFs del directorio actual"""
    directorio_actual = os.getcwd()
    archivos_pdf = glob.glob(os.path.join(directorio_actual, "*.pdf"))
    
    pdfs_cargados = {}
    for archivo_pdf in archivos_pdf:
        nombre_archivo = os.path.basename(archivo_pdf)
        contenido = leer_archivo(archivo_pdf)
        
        if not contenido.startswith("Error"):
            pdfs_cargados[nombre_archivo] = contenido
            print(f"[OK] PDF cargado: {nombre_archivo}")
        else:
            print(f"[ERROR] Error cargando: {nombre_archivo}")
    
    return pdfs_cargados

def inicializar_base_datos():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect('contrataciones.db')
    cursor = conn.cursor()
    
    # Leer y ejecutar el archivo SQL
    with open('contrataciones.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
        cursor.executescript(sql_content)
    
    conn.commit()
    conn.close()

def verificar_disponibilidad(dj_nombre, fecha_evento):
    """Verifica si un DJ está disponible en una fecha específica"""
    conn = sqlite3.connect('contrataciones.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM contrataciones 
        WHERE dj_nombre = ? AND fecha_evento = ? AND estado = 'confirmada'
    """, (dj_nombre, fecha_evento))
    
    resultado = cursor.fetchone()[0]
    conn.close()
    
    return resultado == 0  # True si está disponible (no hay contrataciones)

def guardar_contratacion(dj, datos, precio_total):
    """Guarda una contratación en la base de datos"""
    conn = sqlite3.connect('contrataciones.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO contrataciones 
        (dj_nombre, cliente_nombre, cliente_telefono, cliente_email, 
         localizacion, fecha_evento, duracion, precio_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dj,
        datos['nombre'],
        datos['telefono'],
        datos['email'],
        datos['localizacion'],
        datos['fecha'],
        datos['duracion'],
        precio_total
    ))
    
    conn.commit()
    conn.close()

def manager_dj_booking():
    """Manager de DJs que sigue exactamente las instrucciones del prompt PDF"""
    print("\n=== FUNNDICATION DJ BOOKINGS ===")
    print("Cargando base de conocimientos...")
    
    # Inicializar base de datos
    inicializar_base_datos()
    print("[OK] Base de datos inicializada")
    
    # Cargar PDFs automáticamente
    pdfs = cargar_pdfs_directorio()
    
    if len(pdfs) < 2:
        print("Error: Se necesitan al menos 2 PDFs (prompt + documentación)")
        return
    
    # Identificar archivos por nombre
    prompt_instrucciones = None
    djs_database = None
    
    for nombre, contenido in pdfs.items():
        if "prompt" in nombre.lower():
            prompt_instrucciones = contenido
            print(f"[PROMPT] Instrucciones cargadas desde: {nombre}")
        elif "data" in nombre.lower():
            djs_database = contenido
            print(f"[DATA] Base de datos DJs cargada desde: {nombre}")
    
    if not prompt_instrucciones or not djs_database:
        print("Error: No se encontraron los archivos necesarios")
        return
    
    print("\nSoy el mejor manager de DJs especializado en contratacion de artistas.")
    print("Estoy aqui para ayudarte con tu booking. Escribe 'salir' para terminar.\n")
    
    # Estado de la conversación
    dj_seleccionado = None
    datos_evento = {}
    
    while True:
        # Solo preguntar "¿En que puedo ayudarte?" si no hemos seleccionado DJ
        if dj_seleccionado is None:
            pregunta = input("¿En que puedo ayudarte?: ").strip()
        else:
            # Si ya tenemos DJ seleccionado, solo esperar respuesta
            pregunta = input().strip()
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("\nGracias por tu tiempo y te despido de forma cordial y amigable.")
            print("Espero que tengas un evento espectacular!")
            break
            
        if not pregunta:
            print("Por favor, dime en que puedo ayudarte.")
            continue
        
        # Detectar intención de contratación según el prompt
        palabras_booking = ["contratar", "booking", "book", "contratación", "quiero contratar", "me gustaría contratar", "necesito contratar"]
        
        if any(palabra in pregunta.lower() for palabra in palabras_booking):
            print("\n¡Perfecto! Te muestro todos los DJs que tenemos disponibles con toda su informacion:")
            print("=" * 70)
            
            # Mostrar TODA la información exacta del archivo de datos
            mostrar_todos_los_djs(djs_database)
            
            print("=" * 70)
            print("\n¿Cual de estos artistas te interesa contratar?")
            
            # Esperar respuesta del usuario para selección de DJ
            respuesta_dj = input().strip()
            
            if respuesta_dj.lower() in ['salir', 'exit', 'quit']:
                print("\nGracias por tu tiempo y te despido de forma cordial y amigable.")
                break
                
            dj_seleccionado = extraer_nombre_dj(respuesta_dj)
            if dj_seleccionado != "DJ seleccionado":
                print(f"\n¡Excelente eleccion! Has seleccionado a {dj_seleccionado}")
                print("Para cerrar la contratacion necesito los siguientes datos obligatorios:")
                print("+ Localizacion del evento")
                print("+ Fecha del evento")  
                print("+ Duracion de la actuacion")
                print("+ Nombre y apellidos")
                print("+ Telefono")
                print("+ Correo electronico")
                print("\nEmpecemos con el primer dato.")
                print("Localizacion del evento:")
                continue
            else:
                print("No he reconocido ese artista. Por favor, selecciona uno de la lista anterior.")
                continue
            
        # Si menciona un DJ específico después de ver la lista
        elif dj_seleccionado is None and any(dj in pregunta.lower() for dj in ["brainkiller", "jose", "rodriguez", "tortu", "aparicio", "wardian"]):
            dj_seleccionado = extraer_nombre_dj(pregunta)
            print(f"\n¡Excelente eleccion! Has seleccionado a {dj_seleccionado}")
            print("Para cerrar la contratacion necesito los siguientes datos obligatorios:")
            print("+ Localizacion del evento")
            print("+ Fecha del evento")  
            print("+ Duracion de la actuacion")
            print("+ Nombre y apellidos")
            print("+ Telefono")
            print("+ Correo electronico")
            print("\nEmpecemos con el primer dato.")
            print("Localizacion del evento:")
            
        # Recopilar datos del evento
        elif dj_seleccionado and len(datos_evento) < 6:
            resultado = recopilar_datos_evento(datos_evento, pregunta, dj_seleccionado)
            
            # Si la fecha no está disponible, no avanzar y pedir otra fecha
            if not resultado:
                continue
            
            if len(datos_evento) == 6:
                finalizar_contratacion(dj_seleccionado, datos_evento, djs_database)
                break
                
        else:
            # Buscar información específica
            informacion = buscar_en_texto(djs_database, pregunta)
            print(f"\nBasandome en nuestra base de datos: {informacion}")

def mostrar_todos_los_djs(database):
    """Muestra toda la información de los DJs sin resumir ni parafrasear"""
    lineas = database.split('\n')
    dj_info = ""
    
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith("NOMBRE:"):
            if dj_info:
                print(dj_info)
                print("-" * 50)
            dj_info = linea + "\n"
        elif linea and not linea.startswith("CHATBOT") and not linea.startswith("ARTISTAS:") and not linea.startswith("INGRESOS") and not linea.startswith("PRESS"):
            dj_info += linea + "\n"
    
    if dj_info:
        print(dj_info)

def extraer_nombre_dj(pregunta):
    """Extrae el nombre del DJ de la pregunta"""
    pregunta_lower = pregunta.lower()
    if "brainkiller" in pregunta_lower:
        return "The Brainkiller"
    elif "jose" in pregunta_lower or "rodriguez" in pregunta_lower:
        return "Jose Rodriguez"
    elif "tortu" in pregunta_lower:
        return "Tortu"
    elif "aparicio" in pregunta_lower:
        return "V. Aparicio"
    elif "wardian" in pregunta_lower:
        return "Wardian"
    return "DJ seleccionado"

def recopilar_datos_evento(datos, respuesta, dj_nombre=None):
    """Recopila los datos del evento paso a paso"""
    campos = ["localizacion", "fecha", "duracion", "nombre", "telefono", "email"]
    campo_actual = campos[len(datos)]
    
    # Verificar disponibilidad cuando se introduce la fecha
    if campo_actual == "fecha" and dj_nombre:
        if not verificar_disponibilidad(dj_nombre, respuesta):
            print(f"\n❌ Lo siento, {dj_nombre} no está disponible el {respuesta}")
            print("Esa fecha ya está ocupada. Por favor, elige otra fecha.")
            return False  # Indica que hay que repetir este campo
    
    datos[campo_actual] = respuesta
    print(f"[OK] {campo_actual.capitalize()}: {respuesta}")
    
    if len(datos) < 6:
        siguiente_campo = campos[len(datos)]
        nombres_campos = {
            "localizacion": "Localizacion del evento",
            "fecha": "Fecha del evento", 
            "duracion": "Duracion de la actuacion",
            "nombre": "Nombre y apellidos",
            "telefono": "Telefono",
            "email": "Correo electronico"
        }
        print(f"\nAhora necesito: {nombres_campos[siguiente_campo]}")
    
    return True  # Indica que el campo se completó correctamente

def finalizar_contratacion(dj, datos, database):
    """Finaliza la contratación con desglose de precio"""
    print(f"\n¡Excelente! He recogido todos los datos para contratar a {dj}")
    print("=" * 50)
    print("RESUMEN DE LA CONTRATACION:")
    print(f"DJ: {dj}")
    print(f"Localizacion: {datos['localizacion']}")
    print(f"Fecha: {datos['fecha']}")
    print(f"Duracion: {datos['duracion']}")
    print(f"Cliente: {datos['nombre']}")
    print(f"Telefono: {datos['telefono']}")
    print(f"Email: {datos['email']}")
    print("=" * 50)
    
    # Calcular precio basado en datos reales del PDF
    print("\nDESGLOSE DEL PRECIO:")
    
    # Precios exactos del PDF - CACHÉ BASE (1 hora)
    precios_djs = {
        "The Brainkiller": {"base": 1600, "fuera_malaga": 1800, "fuera_espana": 2500},
        "Jose Rodriguez": {"base": 1000, "fuera_malaga": 1200, "fuera_espana": 1900},
        "Tortu": {"base": 1200, "fuera_malaga": 1400, "fuera_espana": 2100},
        "V. Aparicio": {"base": 600, "fuera_malaga": 800, "fuera_espana": 1500},
        "Wardian": {"base": 600, "fuera_malaga": 800, "fuera_espana": 1500}
    }
    
    # Obtener precios del DJ seleccionado
    precios_dj = precios_djs.get(dj, precios_djs["V. Aparicio"])
    
    # Determinar precio base según localización
    localizacion = datos['localizacion'].lower()
    
    if "málaga" in localizacion or "malaga" in localizacion:
        precio_base = precios_dj["base"]
        print(f"Caché base {dj} (Málaga): {precio_base}€")
    elif any(pais in localizacion for pais in ["francia", "portugal", "italia", "alemania", "reino unido", "uk", "france", "germany", "italy"]) or "fuera de españa" in localizacion:
        precio_base = precios_dj["fuera_espana"]
        print(f"Caché {dj} fuera de España: {precio_base}€")
        print("(No incluido hotel, desplazamiento y comida)")
    else:
        precio_base = precios_dj["fuera_malaga"]
        print(f"Caché {dj} fuera de Málaga: {precio_base}€")
        print("(No incluido hotel, desplazamiento y comida)")
    
    # Calcular horas adicionales (según PDF: +300€ por cada hora añadida)
    duracion_texto = datos['duracion'].lower()
    horas = 1  # Caché base = 1 hora según PDF
    
    if 'hora' in duracion_texto:
        numeros = re.findall(r'\d+', duracion_texto)
        if numeros:
            horas = int(numeros[0])
    
    precio_horas_extra = 0
    if horas > 1:
        horas_extra = horas - 1
        precio_horas_extra = horas_extra * 300  # 300€ por hora según PDF
        print(f"Horas adicionales ({horas_extra}h x 300€): +{precio_horas_extra}€")
    
    # Cálculo final
    precio_total = precio_base + precio_horas_extra
    
    print("-" * 40)
    print(f"TOTAL: {precio_total}€")
    print("-" * 40)
    
    print(f"\nPara cerrar la contratacion debe hacer el ingreso a la cuenta:")
    print("NUMERO DE CUENTA: 78979566700116362718")
    print("\nRecibira un correo de confirmacion cuando el ingreso sea recibido.")
    print("\nTambien puede descargar los press kits desde:")
    print("https://www.funndarkbookings/presskits.com")
    
    # Guardar la contratación en la base de datos
    guardar_contratacion(dj, datos, precio_total)
    print(f"\n✅ Contratación guardada correctamente en el sistema")
    
    print(f"\n¡Gracias por confiar en nosotros para tu evento con {dj}!")
    print("¡Que tengas un espectaculo increible!")

def asistente_rag():
    """Wrapper para mantener compatibilidad"""
    manager_dj_booking()

def main():
    print("*** BIENVENIDO A FUNNDICATION DJ BOOKINGS ***")
    print("=" * 50)
    asistente_rag()

if __name__ == "__main__":
    main()


