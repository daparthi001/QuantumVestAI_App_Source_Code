import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../client'

export function usePing() {
  return useQuery({
    queryKey: ['ping'],
    queryFn: () => apiFetch<{ message: string }>('/ping'),
  })
}
