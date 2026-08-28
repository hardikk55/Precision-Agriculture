import type { HardwareConnectionStatus } from '../hardware/Esp32Adapter'

export function HardwareStatus({ mode, status, sensorIds }: { mode: 'simulation' | 'hardware'; status: HardwareConnectionStatus; sensorIds: string[] }) {
  const hardware = mode === 'hardware'
  return <section className="hardware-status"><div><p className="eyebrow">HARDWARE LAYER</p><strong>{hardware ? 'Hardware mode' : 'Simulation mode'}</strong></div><div className={hardware ? 'hardware-state offline' : 'hardware-state'}><span>ESP32</span><b>{hardware ? 'Disconnected' : 'Standby'}</b></div><div className="hardware-state"><span>Sensors</span><b>{hardware ? `${status.sensorsActive}/9 active` : '9/9 active'}</b></div><div className="hardware-state"><span>Actuator</span><b>{hardware ? 'Unavailable' : 'Virtual ready'}</b></div><div className="sensor-map" aria-label="Sensor mapping overview">{sensorIds.map((id) => <span key={id}>{id}</span>)}</div></section>
}
