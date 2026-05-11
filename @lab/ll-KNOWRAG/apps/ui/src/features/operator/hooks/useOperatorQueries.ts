import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  getHealth,
  postReconcile,
  type HealthResponse,
  type ReconcileResponse,
} from '../services/operatorService'

export function useHealth() {
  return useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: getHealth,
    refetchInterval: 30_000,
    staleTime: 10_000,
    retry: 1,
    refetchOnWindowFocus: false,
  })
}

export function useReconcileMutation() {
  const queryClient = useQueryClient()
  return useMutation<ReconcileResponse, Error, void>({
    mutationFn: postReconcile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['artifacts'] })
      queryClient.invalidateQueries({ queryKey: ['search'] })
    },
  })
}
