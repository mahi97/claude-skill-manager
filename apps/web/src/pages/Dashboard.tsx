import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { StatusCard } from '../components/StatusCard'
import { ItemTable } from '../components/ItemTable'

export function Dashboard() {
  const { data: status } = useQuery({ queryKey: ['status'], queryFn: api.getStatus })
  const { data: candidates } = useQuery({ queryKey: ['candidates'], queryFn: api.getCandidates })

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Dashboard</h2>

      {status && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          <StatusCard label="Installed" value={status.installed} color="green" />
          <StatusCard label="Candidates" value={status.candidates} color="yellow" />
          <StatusCard label="Rejected" value={status.rejected} color="red" />
          <StatusCard label="Proposals" value={status.proposals} color="purple" />
          <StatusCard label="Sources" value={status.sources} color="blue" />
          <StatusCard label="Evaluations" value={status.evaluations} color="cyan" />
          <StatusCard label="Snapshots" value={status.snapshots} color="blue" />
        </div>
      )}

      {candidates && candidates.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 text-yellow-400">Pending Candidates</h3>
          <ItemTable items={candidates} />
        </div>
      )}
    </div>
  )
}
