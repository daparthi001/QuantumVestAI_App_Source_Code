const API_BASE = '/api'

export async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, options)
  if (!res.ok) {
    throw new Error('Network response was not ok')
  }
  return res.json() as Promise<T>
}
