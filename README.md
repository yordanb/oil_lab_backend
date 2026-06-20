# project-oil-lab-be

Backend API untuk Oil Lab — analisa sampel oil.

## Stack

- Python 3.12 + FastAPI
- TimescaleDB (PostgreSQL 16)
- Docker Compose

## Struktur

```
api/                    # Backend API
  app/
    main.py             # Entry point
    core/database.py    # DB connection
    api/v1/             # REST endpoints
    services/           # Business logic
    models/             # SQLAlchemy models
    schemas/            # Pydantic schemas
db/                     # DB init scripts
docker-compose.yml
Dockerfile
```

## API Endpoints

| Method | Path               | Fungsi                |
|--------|--------------------|-----------------------|
| GET    | `/`                | Root status           |
| GET    | `/health`          | Health check          |
| GET    | `/api/samples`     | List samples          |
| GET    | `/api/samples/stats`  | Statistik dashboard |
| GET    | `/api/samples/units`  | Daftar unit unik    |
| GET    | `/api/samples/search` | Sample by filter    |
| GET    | `/api/samples/{id}`   | Detail sample       |
| GET    | `/api/samples/unit/{unit_id}` | By unit         |
| GET    | `/api/samples/vessel/{vessel_id}` | By vessel      |
| GET    | `/api/import/history` | Riwayat import       |
| POST   | `/api/import/xlsx` | Upload file XLSX      |

## Running

```bash
docker compose up -d
```

## Port

- API: `8009`
- DB: `5433`
