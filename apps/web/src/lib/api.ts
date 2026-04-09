const BASE = '/api'

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function postJSON<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  getStatus: () => fetchJSON<Record<string, number>>('/status'),
  getItems: (params?: string) => fetchJSON<any[]>(`/items${params ? `?${params}` : ''}`),
  getInstalled: () => fetchJSON<any[]>('/items/installed'),
  getCandidates: () => fetchJSON<any[]>('/items/candidates'),
  getItem: (id: string) => fetchJSON<any>(`/items/${id}`),
  search: (q: string) => fetchJSON<any[]>(`/search?q=${encodeURIComponent(q)}`),
  compare: (a: string, b: string) => fetchJSON<any>(`/items/${a}/compare/${b}`),
  getSources: () => fetchJSON<any[]>('/sources'),
  getGraph: () => fetchJSON<{ nodes: any[]; edges: any[] }>('/graph'),
  getProposals: () => fetchJSON<any[]>('/proposals'),
  getProposal: (id: string) => fetchJSON<any>(`/proposals/${id}`),
  applyProposal: (id: string) => postJSON<any>(`/proposals/${id}/apply`),
  getEvaluations: () => fetchJSON<any[]>('/evaluations'),
  getSnapshots: () => fetchJSON<any[]>('/snapshots'),
  createSnapshot: (desc?: string) => postJSON<any>(`/snapshots?description=${encodeURIComponent(desc || 'Manual')}`),
  rollback: (id: string) => postJSON<any>(`/snapshots/${id}/rollback`),
  runScout: () => postJSON<any>('/scout'),
  runEvaluate: () => postJSON<any>('/evaluate'),
  runPropose: () => postJSON<any>('/propose'),
  getTaxonomy: () => fetchJSON<any[]>('/taxonomy'),
  getPolicies: () => fetchJSON<any[]>('/policies'),
}
