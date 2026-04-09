import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export function SnapshotsPage() {
  const queryClient = useQueryClient()
  const { data: snapshots, isLoading } = useQuery({ queryKey: ['snapshots'], queryFn: api.getSnapshots })

  const createMutation = useMutation({
    mutationFn: () => api.createSnapshot('Manual snapshot from UI'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['snapshots'] }),
  })

  const rollbackMutation = useMutation({
    mutationFn: api.rollback,
    onSuccess: () => {
      queryClient.invalidateQueries()
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Snapshots</h2>
        <button
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
        >
          Create Snapshot
        </button>
      </div>

      {isLoading ? (
        <p className="text-gray-500">Loading...</p>
      ) : snapshots && snapshots.length > 0 ? (
        <div className="space-y-3">
          {snapshots.map((s: any) => (
            <div key={s.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800 flex items-center justify-between">
              <div>
                <h3 className="font-mono text-sm font-semibold">{s.id}</h3>
                <p className="text-gray-400 text-sm">{s.description}</p>
                <p className="text-gray-600 text-xs mt-1">
                  {new Date(s.created_at).toLocaleString()} &middot; {s.file_manifest?.length || 0} files
                  {s.trigger && ` &middot; ${s.trigger}`}
                </p>
              </div>
              <button
                onClick={() => {
                  if (confirm(`Rollback to ${s.id}? A backup snapshot will be created first.`)) {
                    rollbackMutation.mutate(s.id)
                  }
                }}
                className="px-3 py-1.5 bg-yellow-700 hover:bg-yellow-600 rounded text-sm"
              >
                Rollback
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No snapshots yet.</p>
      )}
    </div>
  )
}
