import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { ItemTable } from '../components/ItemTable'

export function InstalledPage() {
  const { data: items, isLoading } = useQuery({ queryKey: ['installed'], queryFn: api.getInstalled })

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Installed Stack</h2>
      {isLoading ? (
        <p className="text-gray-500">Loading...</p>
      ) : items && items.length > 0 ? (
        <ItemTable items={items} showStatus={false} />
      ) : (
        <p className="text-gray-500">No installed items.</p>
      )}
    </div>
  )
}
