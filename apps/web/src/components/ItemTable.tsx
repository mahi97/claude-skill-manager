import { useNavigate } from 'react-router-dom'

interface ItemTableProps {
  items: any[]
  showStatus?: boolean
}

const trustColors: Record<string, string> = {
  official: 'text-green-400',
  curated: 'text-blue-400',
  community: 'text-yellow-400',
  untrusted: 'text-red-400',
}

const statusColors: Record<string, string> = {
  installed: 'bg-green-900 text-green-300',
  candidate: 'bg-yellow-900 text-yellow-300',
  rejected: 'bg-red-900 text-red-300',
}

export function ItemTable({ items, showStatus = true }: ItemTableProps) {
  const navigate = useNavigate()

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-gray-800">
            <th className="pb-2 pr-4">Name</th>
            <th className="pb-2 pr-4">Type</th>
            {showStatus && <th className="pb-2 pr-4">Status</th>}
            <th className="pb-2 pr-4">Trust</th>
            <th className="pb-2 pr-4">Risk</th>
            <th className="pb-2">Categories</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="border-b border-gray-800/50 hover:bg-gray-900 cursor-pointer"
              onClick={() => navigate(`/items/${item.id}`)}
            >
              <td className="py-2 pr-4 font-medium">{item.name}</td>
              <td className="py-2 pr-4 text-gray-400">{item.type}</td>
              {showStatus && (
                <td className="py-2 pr-4">
                  <span className={`px-2 py-0.5 rounded text-xs ${statusColors[item.status] || ''}`}>
                    {item.status}
                  </span>
                </td>
              )}
              <td className={`py-2 pr-4 ${trustColors[item.trust_tier] || ''}`}>{item.trust_tier}</td>
              <td className="py-2 pr-4 text-gray-400">{item.risk?.score?.toFixed(2)}</td>
              <td className="py-2 text-gray-500">{(item.categories || []).join(', ')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
