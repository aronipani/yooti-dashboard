/**
 * Axios API client for the yooti-dashboard backend.
 * Base URL is configured via VITE_API_BASE_URL environment variable.
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

export { apiClient }
