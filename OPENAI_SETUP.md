# 🤖 Configuración de OpenAI para Funndication DJ Bookings

## 🚀 ¿Qué mejora OpenAI?

Con OpenAI integrado, tu chatbot será **mucho más inteligente**:

✅ **Conversaciones naturales** - Entiende preguntas complejas  
✅ **Mejores recomendaciones** - Sugiere DJs según el evento  
✅ **Respuestas contextuales** - Información detallada y personalizada  
✅ **Detección automática** - Reconoce intenciones sin palabras exactas  

## 🔑 Paso 1: Obtener API Key de OpenAI

1. **Ve a:** [platform.openai.com](https://platform.openai.com)
2. **Crea cuenta** o inicia sesión
3. **Ve a:** API Keys → "Create new secret key"
4. **Copia** la clave que empieza con `sk-...`

## ⚙️ Paso 2: Configurar localmente

1. **Abre el archivo `.env`** en tu proyecto
2. **Reemplaza** `tu_api_key_de_openai_aqui` con tu clave real:
   ```
   OPENAI_API_KEY=sk-tu_clave_real_aqui
   ```
3. **Guarda** el archivo

## 🌐 Paso 3: Configurar en Railway

1. **En Railway dashboard** → Tu proyecto → **Settings** → **Variables**
2. **Añade variable:**
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-tu_clave_real_aqui`
3. **Deploy** automáticamente

## 💰 Costos de OpenAI

- **gpt-3.5-turbo:** ~$0.002 por 1K tokens (muy barato)
- **Estimación:** ~$5-10/mes para uso normal
- **Primer uso:** OpenAI da créditos gratuitos

## 🧪 Cómo probar

**Sin OpenAI (palabras exactas):**
- Usuario: "hola" → "No encontré información..."

**Con OpenAI (inteligente):**
- Usuario: "hola" → "¡Hola! Soy tu manager de DJs..."
- Usuario: "busco música para bodas" → Recomienda DJs y precios
- Usuario: "qué tal está Brainkiller" → Info detallada del artista

## 🔒 Seguridad

- ✅ El archivo `.env` está en `.gitignore`
- ✅ La API key NO se sube a GitHub
- ✅ Solo se usa para el chatbot (no se almacena)

## 🆘 Fallback automático

Si OpenAI falla o no está configurado:
- ✅ El chatbot **sigue funcionando**
- ✅ Usa el sistema original de palabras clave
- ✅ No hay errores para el usuario

---

## 🚀 Para Railway (Opcional)

Si NO quieres usar OpenAI, simplemente:
1. No configures la variable `OPENAI_API_KEY`
2. El sistema funcionará con la lógica original
3. Todo seguirá funcionando perfectamente

¡El chatbot está diseñado para funcionar con o sin OpenAI!