/**
 * AquaPura API service
 *
 * Thin wrapper around fetch for all backend calls.
 *
 * The base URL is read from the Vite environment variable
 * VITE_API_BASE_URL (set in .env or .env.local).
 * During development the Vite proxy forwards /api/* to
 * http://localhost:8000, so the base URL defaults to "" (empty string)
 * which means "same origin" — the proxy handles the rest.
 *
 * In production, set VITE_API_BASE_URL to the deployed backend URL.
 */

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '')

// ── Helper ───────────────────────────────────────────────────────────────────

/**
 * Parse a FastAPI error response into a human-readable message.
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function parseErrorDetail(response) {
  let detail = `Server error ${response.status}`
  try {
    const body = await response.json()
    if (body.detail) {
      detail = Array.isArray(body.detail)
        ? body.detail.map((d) => `${d.loc?.slice(1).join(' → ') ?? 'field'}: ${d.msg}`).join('; ')
        : String(body.detail)
    }
  } catch { /* keep generic message */ }
  return detail
}

/**
 * Shared fetch wrapper that throws a human-readable Error on failure.
 * @param {string} url
 * @param {RequestInit} options
 * @returns {Promise<any>}
 */
async function apiFetch(url, options = {}) {
  let response
  try {
    response = await fetch(url, options)
  } catch {
    throw new Error(
      'Could not reach the AquaPura backend. ' +
        'Make sure the backend server is running on port 8000.',
    )
  }
  if (!response.ok) {
    throw new Error(await parseErrorDetail(response))
  }
  return response.json()
}

// ── Prediction ───────────────────────────────────────────────────────────────

/**
 * Submit a water-quality sample to the prediction endpoint.
 *
 * @param {Object} sample  - Nine numeric fields matching the API schema:
 *   ph, hardness, solids, chloramines, sulfate, conductivity,
 *   organic_carbon, trihalomethanes, turbidity
 *
 * @returns {Promise<{
 *   potable_label: number,
 *   potable: boolean,
 *   probability_potable: number|null,
 *   probability_not_potable: number|null,
 *   disclaimer: string
 * }>}
 */
export function predictPotability(sample) {
  return apiFetch(`${API_BASE}/api/predict`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(sample),
  })
}

// ── Chat ─────────────────────────────────────────────────────────────────────

/**
 * Send a message to the AquaPura AI Assistant.
 *
 * @param {string} message               - User's message text.
 * @param {Object|null} predictionContext - Latest PredictionResponse, or null.
 *
 * @returns {Promise<{ reply: string, disclaimer: string }>}
 */
export function sendChatMessage(message, predictionContext = null) {
  const body = { message }
  if (predictionContext !== null) {
    body.prediction_context = {
      potable:                 predictionContext.potable,
      potable_label:           predictionContext.potable_label,
      probability_potable:     predictionContext.probability_potable ?? null,
      probability_not_potable: predictionContext.probability_not_potable ?? null,
    }
  }
  return apiFetch(`${API_BASE}/api/chat`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  })
}

// ── Auth ─────────────────────────────────────────────────────────────────────

/**
 * Register a new user account.
 *
 * @param {{ full_name: string, email: string, password: string }} data
 * @returns {Promise<{ id: number, full_name: string, email: string }>}
 */
export function registerUser(data) {
  return apiFetch(`${API_BASE}/api/auth/register`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data),
  })
}

/**
 * Log in and retrieve a JWT access token.
 *
 * @param {{ email: string, password: string }} data
 * @returns {Promise<{ access_token: string, token_type: string }>}
 */
export function loginUser(data) {
  return apiFetch(`${API_BASE}/api/auth/login`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data),
  })
}

// ── User profile ─────────────────────────────────────────────────────────────

/**
 * Fetch the current user's profile.
 *
 * @param {string} token - Bearer JWT
 * @returns {Promise<{ id: number, full_name: string, email: string }>}
 */
export function fetchMe(token) {
  return apiFetch(`${API_BASE}/api/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}

// ── Analysis history ─────────────────────────────────────────────────────────

/**
 * Save an analysis result for the authenticated user.
 *
 * @param {string} token - Bearer JWT
 * @param {Object} data  - AnalysisCreate payload
 * @returns {Promise<Object>} Saved AnalysisResponse
 */
export function saveAnalysis(token, data) {
  return apiFetch(`${API_BASE}/api/users/me/analyses`, {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization:  `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}

/**
 * Fetch all saved analyses for the authenticated user.
 *
 * @param {string} token - Bearer JWT
 * @returns {Promise<Object[]>} List of AnalysisResponse objects
 */
export function fetchAnalyses(token) {
  return apiFetch(`${API_BASE}/api/users/me/analyses`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}
