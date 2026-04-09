import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export function SourcesPage() {
  const queryClient = useQueryClient()
  const { data: sources, isLoading } = useQuery({ queryKey: ['sources'], queryFn: api.getSources })
  const scoutMutation = useMutation({
    mutationFn: api.runScout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      queryClient.invalidateQueries({ queryKey: ['status'] })
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Sources</h2>
        <button
          onClick={() => scoutMutation.mutate()}
          disabled={scoutMutation.isPending}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
        >
          {scoutMutation.isPending ? 'Scouting...' : 'Scout All'}
        </button>
      </div>

      {scoutMutation.data && (
        <div className="bg-green-900/30 border border-green-800 rounded p-3 text-sm">
          Scout complete: {scoutMutation.data.total_new} new candidates found
        </div>
      )}

      {isLoading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <div className="space-y-3">
          {sources?.map((s: any) => (
            <div key={s.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{s.name}</h3>
                  <p className="text-gray-400 text-sm">{s.url}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{s.type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${s.enabled ? 'bg-green-900 text-green-300' : 'bg-gray-800 text-gray-500'}`}>
                    {s.enabled ? 'enabled' : 'disabled'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {s.last_synced_at ? `Synced: ${new Date(s.last_synced_at).toLocaleString()}` : 'Never synced'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
