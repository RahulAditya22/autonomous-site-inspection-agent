# API

- `GET /api/health`
- `GET /api/drones`
- `GET /api/missions`
- `POST /api/missions` with `{objective, drone_id}`
- `GET /api/missions/:id`
- `POST /api/missions/:id/start`
- `POST /api/missions/:id/demo`
- `POST /api/missions/:id/approval` with `{approved}`
- `GET /api/missions/:id/report`
- `GET /api/rag?q=...`
- `POST /api/memory/query` with `{question}`
- `POST /api/inspections/analyze` multipart field `image` (JPG/PNG/WEBP; configured size limit)
