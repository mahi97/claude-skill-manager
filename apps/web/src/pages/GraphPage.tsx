import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { api } from '../lib/api'

const typeColors: Record<string, string> = {
  plugin: '#3b82f6',
  skill: '#10b981',
  hook: '#f59e0b',
  mcp_server: '#8b5cf6',
  subagent: '#ec4899',
  marketplace: '#06b6d4',
  source_repo: '#6366f1',
}

const statusStyles: Record<string, { border: string }> = {
  installed: { border: '2px solid #22c55e' },
  candidate: { border: '2px dashed #eab308' },
  rejected: { border: '2px dotted #ef4444' },
}

export function GraphPage() {
  const { data: graphData, isLoading } = useQuery({ queryKey: ['graph'], queryFn: api.getGraph })

  const { initialNodes, initialEdges } = useMemo(() => {
    if (!graphData) return { initialNodes: [], initialEdges: [] }

    const nodes: Node[] = graphData.nodes.map((n: any, i: number) => {
      const cols = Math.ceil(Math.sqrt(graphData.nodes.length))
      const row = Math.floor(i / cols)
      const col = i % cols
      return {
        id: n.id,
        position: { x: col * 250, y: row * 150 },
        data: {
          label: `${n.data.label}\n[${n.data.type}]`,
        },
        style: {
          background: typeColors[n.data.type] || '#6b7280',
          color: '#fff',
          padding: '8px 16px',
          borderRadius: '8px',
          fontSize: '12px',
          ...(statusStyles[n.data.status] || {}),
        },
      }
    })

    const edges: Edge[] = graphData.edges.map((e: any) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label,
      style: { stroke: '#6b7280' },
      labelStyle: { fill: '#9ca3af', fontSize: 10 },
    }))

    return { initialNodes: nodes, initialEdges: edges }
  }, [graphData])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  if (isLoading) return <p className="text-gray-500">Loading graph...</p>

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Registry Graph</h2>
      <div className="flex gap-4 text-xs text-gray-500">
        {Object.entries(typeColors).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1">
            <span className="w-3 h-3 rounded" style={{ background: color }} />
            {type}
          </span>
        ))}
      </div>
      <div className="h-[600px] bg-gray-900 rounded-lg border border-gray-800">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          colorMode="dark"
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  )
}
