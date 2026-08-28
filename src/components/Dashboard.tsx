import type { Farm } from '../models/farm'

export function Dashboard({ farm }: { farm: Farm }) {
  const patches = farm.patches; const avg = (key: 'soilMoisture' | 'temperature' | 'humidity') => patches.reduce((sum, patch) => sum + patch[key], 0) / patches.length
  const cards = [
    ['Total patches', String(patches.length), '3 × 3 mapped farm'], ['Needs irrigation', String(patches.filter((p) => p.irrigationRequired).length), 'rule-based decision'], ['Irrigating now', String(patches.filter((p) => p.irrigationStatus === 'irrigating').length), 'virtual solenoids'],
    ['Avg. soil moisture', `${avg('soilMoisture').toFixed(1)}%`, 'across all patches'], ['Avg. temperature', `${avg('temperature').toFixed(1)}°C`, 'simulated sensor data'], ['Avg. humidity', `${avg('humidity').toFixed(1)}%`, 'simulated sensor data'], ['Total water used', `${patches.reduce((sum, p) => sum + p.cumulativeWaterUsed, 0).toFixed(1)} L`, 'irrigation actions'],
  ]
  return <section className="dashboard">{cards.map(([label, value, caption]) => <div className="stat" key={label}><span>{label}</span><strong>{value}</strong><small>{caption}</small></div>)}</section>
}
