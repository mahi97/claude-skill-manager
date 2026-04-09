interface StatusCardProps {
  label: string
  value: number | string
  color?: string
}

export function StatusCard({ label, value, color = 'blue' }: StatusCardProps) {
  const colorMap: Record<string, string> = {
    blue: 'border-blue-500 text-blue-400',
    green: 'border-green-500 text-green-400',
    yellow: 'border-yellow-500 text-yellow-400',
    red: 'border-red-500 text-red-400',
    purple: 'border-purple-500 text-purple-400',
    cyan: 'border-cyan-500 text-cyan-400',
  }

  return (
    <div className={`bg-gray-900 border-l-4 ${colorMap[color] || colorMap.blue} rounded-lg p-4`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-400 mt-1">{label}</div>
    </div>
  )
}
