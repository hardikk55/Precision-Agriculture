import { useState } from 'react'
import { ActivityLog } from './components/ActivityLog'
import { Dashboard } from './components/Dashboard'
import { FarmGrid } from './components/FarmGrid'
import { PatchDetails } from './components/PatchDetails'
import { farmConfig, type Patch } from './models/farm'
import { useFarmSimulation } from './state/useFarmSimulation'

export default function App() {
  const simulation = useFarmSimulation(); const [selectedId, setSelectedId] = useState<string | null>('patch-1-1')
  const selected = simulation.farm.patches.find((patch) => patch.id === selectedId) ?? null
  const select = (patch: Patch) => setSelectedId(patch.id)
  return <main><header><div className="brand"><span className="mark">▦</span><div><p>PRECISION AGRICULTURE RESEARCH</p><h1>Digital Farm <em>01</em></h1></div></div><div className="simulated"><span /> Simulated prototype data</div></header>
    <section className="control-bar"><div><p className="eyebrow">FARM CLOCK</p><strong>{simulation.simulationTime.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} · {simulation.simulationTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong></div><div className="controls"><button onClick={() => simulation.setRunning(!simulation.running)} className={simulation.running ? 'pause' : 'start'}>{simulation.running ? 'Pause' : 'Start'}</button><button className="reset" onClick={simulation.reset}>Reset</button><div className="speed">{[1, 2, 5].map((value) => <button key={value} className={simulation.speed === value ? 'active' : ''} onClick={() => simulation.setSpeed(value)}>{value}×</button>)}</div></div></section>
    <Dashboard farm={simulation.farm} />
    <section className="workspace"><FarmGrid patches={simulation.farm.patches} selectedId={selectedId} onSelect={select} /><PatchDetails patch={selected} onIrrigate={() => selected && simulation.irrigate(selected.row, selected.column)} /></section>
    <ActivityLog events={simulation.events} />
    <footer><span>Prof. Lalit Kumar · University Precision Agriculture Project</span><span>Simulation parameters: threshold {farmConfig.moistureThreshold}% · {farmConfig.irrigationWaterLitres} L / irrigation</span></footer>
  </main>
}
