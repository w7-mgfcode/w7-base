import { useMutation, useQueryClient } from '@tanstack/react-query'
import { postRagQuery, RagQueryResult } from '../services/ragService'
import type { RagQueryRequest } from '../types'

export const RAG_LAST_SUCCESS_KEY = ['rag', 'last-success'] as const

export function useRagQuery() {
  const queryClient = useQueryClient()
  return useMutation<RagQueryResult, Error, RagQueryRequest>({
    mutationFn: postRagQuery,
    onSuccess: (result) => {
      if (result.ok) {
        queryClient.setQueryData(RAG_LAST_SUCCESS_KEY, result.data)
      }
    },
  })
}
