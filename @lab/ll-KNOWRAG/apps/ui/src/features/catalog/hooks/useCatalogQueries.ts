import { useQuery } from '@tanstack/react-query'
import {
  getArtifact,
  getRelatedArtifacts,
  listArtifacts,
  searchArtifacts,
  SearchArgs,
} from '../services/artifactService'
import { ArtifactCategory } from '../types'

export function useArtifacts(category?: ArtifactCategory) {
  return useQuery({
    queryKey: ['artifacts', { category: category ?? null }],
    queryFn: () => listArtifacts(category),
    staleTime: 30_000,
  })
}

export function useArtifact(path: string | null, ref?: string) {
  return useQuery({
    queryKey: ['artifact', path, ref ?? null],
    queryFn: () => getArtifact(path as string, ref),
    enabled: !!path,
    staleTime: 30_000,
  })
}

export function useRelatedArtifacts(
  path: string | null,
  k = 5,
  visibility: 'public' | 'private' = 'public',
) {
  return useQuery({
    queryKey: ['related', path, k, visibility],
    queryFn: () => getRelatedArtifacts(path as string, k, visibility),
    enabled: !!path,
    staleTime: 60_000,
  })
}

export function useArtifactSearch(args: SearchArgs | null) {
  return useQuery({
    queryKey: ['search', args],
    queryFn: () => searchArtifacts(args as SearchArgs),
    enabled: !!args && args.query.trim().length > 0,
    staleTime: 10_000,
  })
}
