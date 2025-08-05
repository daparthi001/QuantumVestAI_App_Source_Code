// Allow overriding the API base URL at build time while defaulting
// to the standard `/api` prefix used in production.
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export async function apiFetch<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    credentials: 'include',
    ...options,
    headers: new Headers(options.headers),
  })
  if (!res.ok) {
    // Surface the server's response body when available to aid debugging
    const message = await res.text()
    throw new Error(message || 'Network response was not ok')
  }
  return res.json() as Promise<T>
}

