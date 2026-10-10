# AquaPura — API Reference

> **Status:** Draft — endpoints will be documented as they are implemented.

Base URL (local): `http://localhost:8000`  
Interactive docs (auto-generated): `http://localhost:8000/docs`

---

## Endpoints

### `POST /api/predict`

Run a water-quality potability prediction.

**Request body** (`application/json`)

| Field | Type | Description |
|---|---|---|
| `ph` | float | pH value (0–14) |
| `hardness` | float | Water hardness (mg/L) |
| `solids` | float | Total dissolved solids (ppm) |
| `chloramines` | float | Chloramines concentration (ppm) |
| `sulfate` | float | Sulfate concentration (mg/L) |
| `conductivity` | float | Electrical conductivity (μS/cm) |
| `organic_carbon` | float | Organic carbon (ppm) |
| `trihalomethanes` | float | Trihalomethanes (μg/L) |
| `turbidity` | float | Turbidity (NTU) |

**Response** `200 OK`

```json
{
  "potable": true,
  "confidence": 0.84,
  "feature_importance": [
    { "feature": "ph", "importance": 0.21 },
    { "feature": "sulfate", "importance": 0.18 }
  ]
}
```

---

### `POST /api/assess`

Save an assessment result to history.

> To be documented when implemented.

---

### `GET /api/history`

Retrieve paginated assessment history.

> To be documented when implemented.

---

### `DELETE /api/history/{id}`

Delete a specific assessment record.

> To be documented when implemented.

---

### `POST /api/chat`

Send a message to the AI water-safety chatbot.

> To be documented when the chatbot feature is implemented.

---

## Error Responses

| Status | Meaning |
|---|---|
| `422 Unprocessable Entity` | Request body failed Pydantic validation |
| `500 Internal Server Error` | Unexpected server-side error |
