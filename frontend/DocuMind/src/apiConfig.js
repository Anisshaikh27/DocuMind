/**
 * Central API base URL.
 *
 * - In development (Vite dev server, npm run dev) the env var
 *   VITE_API_URL is expected to be set (e.g. http://localhost:8000).
 * - In production (Docker / HF Spaces) the frontend is served by the
 *   same FastAPI process, so API calls are relative to the same origin.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL ?? ''

export default API_BASE_URL
