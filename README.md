# Funndication DJ Bookings

Intelligent DJ booking system with AI integration to manage bookings, availability, and pricing automatically.

## Description

Funndication DJ Bookings is a web application that facilitates the booking of DJs specialized in Break Beat. The system uses artificial intelligence (OpenAI) to maintain natural conversations with clients, manage artist availability, and automatically calculate prices based on location and event duration.

## Features

- **Intelligent AI Chat**: Natural conversations using OpenAI GPT to analyze intentions and respond to queries
- **Availability Management**: Database system to verify occupied dates in real-time
- **Automatic Price Calculation**: Differentiated rates by location (Málaga, outside Málaga, international)
- **Data Collection**: Guided flow to obtain event and client information
- **Knowledge Base**: Information extraction from PDFs with artist data
- **REST API**: FastAPI backend with documented endpoints
- **Web Interface**: Modern frontend with interactive chat
- **Data Persistence**: SQLite database to store bookings

## Technologies

### Backend
- **Python 3.x**
- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: ASGI server
- **SQLite**: Embedded database
- **PyPDF2**: Text extraction from PDFs
- **OpenAI API**: Artificial intelligence integration
- **Pydantic**: Data validation

### Frontend
- HTML5, CSS3, JavaScript
- Interactive chat interface

### Deployment
- Compatible with Railway, Heroku, and similar services
- Production-ready configuration

## Project Structure

```
TestingClaudeCode/
├── app.py                      # Main FastAPI API
├── main.py                     # Chatbot logic and processing
├── openai_handler.py           # OpenAI integration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── Procfile                   # Deployment configuration
├── railway.json               # Railway configuration
├── contrataciones.sql         # Database schema
├── contrataciones.db          # SQLite database
├── ChatBotFunndicationData.pdf       # Knowledge base (DJs)
├── ChatBotFunndicationPrompt.pdf     # Chatbot instructions
├── static/                    # Frontend files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── demo.html                  # Standalone demo
└── tests/                     # Test scripts
    ├── test_server.py
    ├── test_flow.py
    └── simple_test.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI account with API key (optional but recommended)

### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd TestingClaudeCode
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
```bash
cp .env.example .env
```

Edit [.env](.env) and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

6. **Initialize database**

The database initializes automatically when starting the application. The schema is defined in [contrataciones.sql](contrataciones.sql).

## Usage

### Web Mode (Production)

Start the FastAPI server:
```bash
python app.py
```

Or with uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at: `http://localhost:8000`

### CLI Mode (Development)

Run the chatbot in command line:
```bash
python main.py
```

### API Endpoints

#### POST `/chat`
Send message to chatbot

**Request:**
```json
{
  "message": "I want to book a DJ",
  "session_id": "optional-uuid"
}
```

**Response:**
```json
{
  "response": "Perfect! I'll show you all the DJs...",
  "session_id": "session-uuid",
  "status": "active"
}
```

#### GET `/health`
Verify service status

**Response:**
```json
{
  "status": "healthy",
  "message": "Funndication DJ Bookings API is running"
}
```

## Available Artists

The system manages 5 DJs specialized in Break Beat:

- **The Brainkiller**: €1,600 (Málaga) / €1,800 (outside Málaga) / €2,500 (international)
- **Jose Rodriguez**: €1,000 / €1,200 / €1,900
- **Tortu**: €1,200 / €1,400 / €2,100
- **V. Aparicio**: €600 / €800 / €1,500
- **Wardian**: €600 / €800 / €1,500

**Base prices:** 1 hour performance
**Additional hours:** +€300 per hour

## Booking Flow

1. **Conversation start**: User expresses interest in booking
2. **DJ selection**: All artists are shown with complete information
3. **Data collection**:
   - Event location
   - Date (with availability verification)
   - Performance duration
   - Client's first and last name
   - Phone number
   - Email address
4. **Price calculation**: Automatic based on DJ, location, and duration
5. **Summary and confirmation**: Complete booking details
6. **Database storage**: Persistent transaction record

## Database

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

## OpenAI Integration

The system can work with or without OpenAI:

**With OpenAI** (recommended):
- Natural conversations
- Intent analysis
- Contextual responses
- Entity extraction

**Without OpenAI** (fallback):
- Keyword-based system
- Predefined responses
- Basic functionality guaranteed

Integration is managed in [openai_handler.py](openai_handler.py:1-219).

## Deployment

### Railway

1. Connect repository to Railway
2. Configure environment variables in the dashboard
3. Railway will automatically detect [Procfile](Procfile) and [railway.json](railway.json)
4. Automatic deployment

### Heroku

```bash
heroku create app-name
heroku config:set OPENAI_API_KEY=your_api_key
git push heroku main
```

### Required environment variables

```env
OPENAI_API_KEY=sk-...        # Required for AI
OPENAI_MODEL=gpt-3.5-turbo   # Optional
PORT=8000                     # Port (auto on Railway/Heroku)
```

## Testing

Run tests:
```bash
# Basic server test
python test_server.py

# Complete flow test
python test_flow.py

# Simple test
python simple_test.py
```

## Additional Documentation

- [OPENAI_SETUP.md](OPENAI_SETUP.md): OpenAI configuration guide
- [FILES_TO_UPLOAD.md](FILES_TO_UPLOAD.md): Files needed for deployment
- [GIT_COMMANDS.md](GIT_COMMANDS.md): Useful Git commands

## Security

- API keys loaded from environment variables
- `.env` file included in `.gitignore`
- Data validation with Pydantic
- Sessions isolated by UUID
- Real-time availability verification

## Future Improvements

- [ ] User authentication
- [ ] Administration panel
- [ ] Automatic email notifications
- [ ] Calendar integration
- [ ] Online payment system
- [ ] Multi-language support
- [ ] Analytics and reports
- [ ] Webhooks for integrations

## Contributions

Contributions are welcome. Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-functionality`)
3. Commit changes (`git commit -am 'Add new functionality'`)
4. Push to branch (`git push origin feature/new-functionality`)
5. Create Pull Request

## License

This project is private and property of Funndication Bookings.

## Contact

For support or system inquiries:
- Email: info@funndication.com
- Press Kits: https://www.funndarkbookings/presskits.com
- Account number: 78979566700116362718

---

**Developed with FastAPI and OpenAI** | **Specialized in Break Beat DJs**
