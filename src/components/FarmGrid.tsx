import type { Patch } from '../models/farm'

interface Props { patches: Patch[]; selectedId: string | null; onSelect: (patch: Patch) => void }
const moistureClass = (value: number) => value < 30 ? 'dry' : value < 50 ? 'balanced' : 'wet'

export function FarmGrid({ patches, selectedId, onSelect }: Props) {
  return <section className="farm-card"><div className="section-heading"><div><p className="eyebrow">DIGITAL TWIN • 1:1 PATCH MAP</p><h2>3 × 3 digital farm</h2></div><div className="legend"><span><i className="dry-dot" /> Needs water</span><span><i className="balanced-dot" /> Balanced</span><span><i className="wet-dot" /> Wet</span></div></div>
    <div className="farm-grid">{patches.map((patch) => <button key={patch.id} className={`patch ${moistureClass(patch.soilMoisture)} ${selectedId === patch.id ? 'selected' : ''}`} onClick={() => onSelect(patch)}>
      <span className="coordinate">({patch.row},{patch.column})</span><strong>{patch.soilMoisture}%</strong><span className="metric-label">soil moisture</span>
      <span className="patch-footer"><span>{patch.temperature}°C</span><span>{patch.humidity}% RH</span></span>
      {patch.irrigationRequired && <span className="needs-water">IRRIGATION REQUIRED</span>}
    </button>)}</div>
  </section>
}
