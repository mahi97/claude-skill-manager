import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

const trustColors: Record<string, string> = {
  official: 'text-green-400',
  curated: 'text-blue-400',
  community: 'text-yellow-400',
  untrusted: 'text-red-400',
}

export function ItemDetail() {
  const { itemId } = useParams<{ itemId: string }>()
  const navigate = useNavigate()
  const { data: item, isLoading, error } = useQuery({
    queryKey: ['item', itemId],
    queryFn: () => api.getItem(itemId!),
    enabled: !!itemId,
  })

  if (isLoading) return <p className="text-gray-500">Loading...</p>
  if (error || !item) return <p className="text-red-400">Item not found.</p>

  return (
    <div className="space-y-6">
      <button onClick={() => navigate(-1)} className="text-sm text-gray-500 hover:text-white">
        &larr; Back
      </button>

      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold">{item.name}</h2>
            <p className="text-gray-400 mt-1">{item.description}</p>
          </div>
          <div className="flex gap-2">
            <span className="text-xs px-2 py-1 bg-gray-800 rounded">{item.type}</span>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded">{item.status}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <Section title="Trust & Risk">
            <Row label="Trust Tier" value={item.trust_tier} className={trustColors[item.trust_tier]} />
            <Row label="Risk Score" value={item.risk?.score?.toFixed(2)} />
            {item.risk?.flags?.length > 0 && (
              <div>
                <span className="text-gray-500">Risk Flags: </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {item.risk.flags.map((f: string) => (
                    <span key={f} className="text-xs px-2 py-0.5 bg-red-900/50 text-red-300 rounded">{f}</span>
                  ))}
                </div>
              </div>
            )}
          </Section>

          <Section title="Provenance">
            <Row label="Source URL" value={item.source_url} />
            <Row label="Repo URL" value={item.repo_url} />
            <Row label="Version" value={item.version} />
            <Row label="Last Seen" value={item.last_seen_at ? new Date(item.last_seen_at).toLocaleString() : 'Unknown'} />
          </Section>

          <Section title="Categories">
            <div className="flex flex-wrap gap-1">
              {(item.categories || []).map((c: string) => (
                <span key={c} className="text-xs px-2 py-0.5 bg-blue-900/50 text-blue-300 rounded">{c}</span>
              ))}
            </div>
          </Section>

          <Section title="Relationships">
            {item.relationships?.length > 0 ? (
              <div className="space-y-1">
                {item.relationships.map((r: any, i: number) => (
                  <div key={i} className="text-gray-400">
                    <span className="text-gray-300">{r.type}</span> &rarr; {r.target_id}
                    {r.notes && <span className="text-gray-600 ml-2">({r.notes})</span>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">None</p>
            )}
          </Section>
        </div>

        {item.local_notes && (
          <div className="mt-6 p-4 bg-gray-800 rounded">
            <h4 className="text-sm text-gray-500 mb-1">Notes</h4>
            <p className="text-gray-300 text-sm">{item.local_notes}</p>
          </div>
        )}
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-gray-500 font-medium mb-2 uppercase text-xs tracking-wider">{title}</h4>
      <div className="space-y-1">{children}</div>
    </div>
  )
}

function Row({ label, value, className = '' }: { label: string; value: string; className?: string }) {
  return (
    <div>
      <span className="text-gray-500">{label}: </span>
      <span className={className || 'text-gray-300'}>{value || 'N/A'}</span>
    </div>
  )
}
