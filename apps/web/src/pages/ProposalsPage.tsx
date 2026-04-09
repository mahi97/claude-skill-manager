import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-900 text-yellow-300',
  approved: 'bg-blue-900 text-blue-300',
  applied: 'bg-green-900 text-green-300',
  rejected: 'bg-red-900 text-red-300',
}

export function ProposalsPage() {
  const queryClient = useQueryClient()
  const { data: proposals, isLoading } = useQuery({ queryKey: ['proposals'], queryFn: api.getProposals })
  const applyMutation = useMutation({
    mutationFn: api.applyProposal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposals'] })
      queryClient.invalidateQueries({ queryKey: ['status'] })
    },
  })

  const generateMutation = useMutation({
    mutationFn: api.runPropose,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['proposals'] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Proposals</h2>
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
        >
          {generateMutation.isPending ? 'Generating...' : 'Generate Proposals'}
        </button>
      </div>

      {isLoading ? (
        <p className="text-gray-500">Loading...</p>
      ) : proposals && proposals.length > 0 ? (
        <div className="space-y-4">
          {proposals.map((p: any) => (
            <div key={p.id} className="bg-gray-900 rounded-lg p-5 border border-gray-800">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-lg">{p.title}</h3>
                  <p className="text-gray-400 text-sm mt-1">{p.summary}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${statusColors[p.status] || ''}`}>
                  {p.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mt-4">
                <div>
                  <div className="text-gray-500 mb-1">Recommendation</div>
                  <div>{p.recommendation}</div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Trust</div>
                  <div>{p.trust_summary}</div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Risk</div>
                  <div className="whitespace-pre-wrap">{p.risk_summary}</div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Overlap</div>
                  <div>{p.overlap_analysis || 'None'}</div>
                </div>
              </div>

              {p.status === 'pending' && (
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => applyMutation.mutate(p.id)}
                    disabled={applyMutation.isPending}
                    className="px-3 py-1.5 bg-green-700 hover:bg-green-600 rounded text-sm disabled:opacity-50"
                  >
                    Apply
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No proposals yet. Run evaluation and generation first.</p>
      )}
    </div>
  )
}
