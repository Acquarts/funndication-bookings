# Funndication DJ Bookings

Sistema inteligente de contratación de DJs con integración de IA para gestionar bookings, disponibilidad y precios de forma automatizada.

## Descripción

Funndication DJ Bookings es una aplicación web que facilita la contratación de DJs especializados en Break Beat. El sistema utiliza inteligencia artificial (OpenAI) para mantener conversaciones naturales con los clientes, gestionar la disponibilidad de artistas y calcular precios automáticamente según localización y duración del evento.

## Características

- **Chat inteligente con IA**: Conversaciones naturales usando OpenAI GPT para analizar intenciones y responder consultas
- **Gestión de disponibilidad**: Sistema de base de datos para verificar fechas ocupadas en tiempo real
- **Cálculo automático de precios**: Tarifas diferenciadas por localización (Málaga, fuera de Málaga, internacional)
- **Recopilación de datos**: Flujo guiado para obtener información del evento y cliente
- **Base de conocimientos**: Extracción de información desde PDFs con datos de artistas
- **API REST**: Backend FastAPI con endpoints documentados
- **Interfaz web**: Frontend moderno con chat interactivo
- **Persistencia de datos**: Base de datos SQLite para almacenar contrataciones

## Tecnologías

### Backend
- **Python 3.x**
- **FastAPI**: Framework web moderno y de alto rendimiento
- **Uvicorn**: Servidor ASGI
- **SQLite**: Base de datos embebida
- **PyPDF2**: Extracción de texto desde PDFs
- **OpenAI API**: Integración de inteligencia artificial
- **Pydantic**: Validación de datos

### Frontend
- HTML5, CSS3, JavaScript
- Interfaz de chat interactiva

### Deployment
- Compatible con Railway, Heroku y servicios similares
- Configuración lista para producción

## Estructura del Proyecto

```
TestingClaudeCode/
├── app.py                      # API FastAPI principal
├── main.py                     # Lógica del chatbot y procesamiento
├── openai_handler.py           # Integración con OpenAI
├── requirements.txt            # Dependencias Python
├── .env.example               # Plantilla de variables de entorno
├── Procfile                   # Configuración para deployment
├── railway.json               # Configuración Railway
├── contrataciones.sql         # Schema de base de datos
├── contrataciones.db          # Base de datos SQLite
├── ChatBotFunndicationData.pdf       # Base de conocimientos (DJs)
├── ChatBotFunndicationPrompt.pdf     # Instrucciones del chatbot
├── static/                    # Archivos frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
├── demo.html                  # Demo standalone
└── tests/                     # Scripts de prueba
    ├── test_server.py
    ├── test_flow.py
    └── simple_test.py
```

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Cuenta OpenAI con API key (opcional pero recomendado)

### Pasos

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd TestingClaudeCode
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar [.env](.env) y añadir tu API key de OpenAI:
```env
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

6. **Inicializar la base de datos**

La base de datos se inicializa automáticamente al arrancar la aplicación. El schema está definido en [contrataciones.sql](contrataciones.sql).

## Uso

### Modo Web (Producción)

Iniciar el servidor FastAPI:
```bash
python app.py
```

O con uvicorn directamente:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

La aplicación estará disponible en: `http://localhost:8000`

### Modo CLI (Desarrollo)

Ejecutar el chatbot en línea de comandos:
```bash
python main.py
```

### Endpoints API

#### POST `/chat`
Enviar mensaje al chatbot

**Request:**
```json
{
  "message": "Quiero contratar un DJ",
  "session_id": "opcional-uuid"
}
```

**Response:**
```json
{
  "response": "¡Perfecto! Te muestro todos los DJs...",
  "session_id": "uuid-de-sesion",
  "status": "active"
}
```

#### GET `/health`
Verificar estado del servicio

**Response:**
```json
{
  "status": "healthy",
  "message": "Funndication DJ Bookings API is running"
}
```

## Artistas Disponibles

El sistema gestiona 5 DJs especializados en Break Beat:

- **The Brainkiller**: 1.600€ (Málaga) / 1.800€ (fuera Málaga) / 2.500€ (internacional)
- **Jose Rodriguez**: 1.000€ / 1.200€ / 1.900€
- **Tortu**: 1.200€ / 1.400€ / 2.100€
- **V. Aparicio**: 600€ / 800€ / 1.500€
- **Wardian**: 600€ / 800€ / 1.500€

**Precios base:** 1 hora de actuación
**Horas adicionales:** +300€ por hora

## Flujo de Contratación

1. **Inicio de conversación**: El usuario expresa interés en contratar
2. **Selección de DJ**: Se muestran todos los artistas con información completa
3. **Recopilación de datos**:
   - Localización del evento
   - Fecha (con verificación de disponibilidad)
   - Duración de la actuación
   - Nombre y apellidos del cliente
   - Teléfono
   - Correo electrónico
4. **Cálculo de precio**: Automático según DJ, localización y duración
5. **Resumen y confirmación**: Detalles completos de la contratación
6. **Guardado en base de datos**: Registro persistente de la transacción

## Base de Datos

Schema: [contrataciones.sql](contrataciones.sql:1-16)

```sql
CREATE TABLE contrataciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dj_nombre TEXT NOT NULL,
    cliente_nombre TEXT NOT NULL,
    cliente_telefono TEXT NOT NULL,
    cliente_email TEXT NOT NULL,
    localizacion TEXT NOT NULL,
    fecha_evento TEXT NOT NULL,
    duracion TEXT NOT NULL,
    precio_total REAL NOT NULL,
    fecha_contratacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'confirmada'
);
```

## Integración con OpenAI

El sistema puede funcionar con o sin OpenAI:

**Con OpenAI** (recomendado):
- Conversaciones naturales
- Análisis de intenciones
- Respuestas contextuales
- Extracción de entidades

**Sin OpenAI** (fallback):
- Sistema basado en palabras clave
- Respuestas predefinidas
- Funcionalidad básica garantizada

La integración se gestiona en [openai_handler.py](openai_handler.py:1-219).

## Deployment

### Railway

1. Conectar repositorio a Railway
2. Configurar variables de entorno en el dashboard
3. Railway detectará automáticamente [Procfile](Procfile) y [railway.json](railway.json)
4. Deploy automático

### Heroku

```bash
heroku create nombre-app
heroku config:set OPENAI_API_KEY=tu_api_key
git push heroku main
```

### Variables de entorno requeridas

```env
OPENAI_API_KEY=sk-...        # Requerido para IA
OPENAI_MODEL=gpt-3.5-turbo   # Opcional
PORT=8000                     # Puerto (auto en Railway/Heroku)
```

## Testing

Ejecutar tests:
```bash
# Test básico del servidor
python test_server.py

# Test de flujo completo
python test_flow.py

# Test simple
python simple_test.py
```

## Documentación Adicional

- [OPENAI_SETUP.md](OPENAI_SETUP.md): Guía de configuración de OpenAI
- [FILES_TO_UPLOAD.md](FILES_TO_UPLOAD.md): Archivos necesarios para deployment
- [GIT_COMMANDS.md](GIT_COMMANDS.md): Comandos Git útiles

## Seguridad

- Las API keys se cargan desde variables de entorno
- Archivo `.env` incluido en `.gitignore`
- Validación de datos con Pydantic
- Sesiones aisladas por UUID
- Verificación de disponibilidad en tiempo real

## Mejoras Futuras

- [ ] Autenticación de usuarios
- [ ] Panel de administración
- [ ] Notificaciones por email automáticas
- [ ] Integración con calendario
- [ ] Sistema de pagos online
- [ ] Soporte multiidioma
- [ ] Analytics y reportes
- [ ] Webhooks para integraciones

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es privado y propiedad de Funndication Bookings.

## Contacto

Para soporte o consultas sobre el sistema:
- Email: info@funndication.com
- Press Kits: https://www.funndarkbookings/presskits.com
- Número de cuenta: 78979566700116362718

---

**Desarrollado con FastAPI y OpenAI** | **Especializado en Break Beat DJs**
