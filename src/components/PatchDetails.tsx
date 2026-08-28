import type { Patch } from '../models/farm'

export function PatchDetails({ patch, onIrrigate }: { patch: Patch | null; onIrrigate: () => void }) {
  if (!patch) return <aside className="details empty"><p>Select a patch from the grid to inspect its live simulated state.</p></aside>
  const fields = [['Soil moisture', `${patch.soilMoisture}%`], ['Temperature', `${patch.temperature} °C`], ['Humidity', `${patch.humidity}% RH`], ['Irrigation requirement', patch.irrigationRequired ? 'Required' : 'Not required'], ['Irrigation status', patch.irrigationStatus], ['Last irrigation', patch.lastIrrigated ?? 'Not yet irrigated'], ['Water used', `${patch.cumulativeWaterUsed.toFixed(1)} L`], ['Data source', patch.dataSource]]
  return <aside className="details"><p className="eyebrow">PATCH INSPECTOR</p><h2>Patch ({patch.row},{patch.column})</h2><div className="details-list">{fields.map(([label, value]) => <div key={label}><span>{label}</span><strong className={value === 'Required' ? 'alert-text' : ''}>{value}</strong></div>)}</div>
    <button className="irrigate-button" onClick={onIrrigate}>Irrigate patch <span>→</span></button><p className="actuator-note">Virtual solenoid • coordinate-specific command</p>
  </aside>
}
