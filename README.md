# GreenPass Agro-Export Backend

🥑 **Infraestructura de Datos para la Verificación Climática EUDR**

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Poetry (optional, recommended) or pip

### Development Setup

```bash
# 1. Clone and enter directory
cd STARTHackathon

# 2. Start PostgreSQL + PostGIS
docker compose up -d

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Run the API
uvicorn src.main:app --reload --port 8000
```

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
src/
├── core/      # 🏛️ Backend 1: Core Orchestrator & Compliance
├── geo/       # 🛰️ Backend 2: Geo-Spatial Engine
├── env/       # 💧 Backend 3: Environmental Impact Engine
├── shared/    # Código compartido
└── db/        # Database layer
```

## API Endpoints

### Public Endpoints (Core)
- `POST /api/projects` - Create new project
- `POST /api/projects/{id}/upload` - Upload GeoJSON
- `GET /api/projects/{id}/report` - Get EUDR DDS Report

### Internal Endpoints (Geo)
- `POST /geo/analyze` - Analyze geometry & deforestation

### Internal Endpoints (Env)
- `POST /env/analyze` - Analyze water & climate risk

## Testing

```bash
pytest tests/ -v
```

## External APIs Used
- [Global Forest Watch](https://data-api.globalforestwatch.org/) - Deforestation alerts
- [Open-Meteo](https://open-meteo.com/) - Historical weather
- [Climatiq](https://www.climatiq.io/) - Carbon emissions
- WRI Aqueduct - Water risk (mocked)

## License
MIT
