import type { SensorStatus } from '../models/farm'

/** Contract expected from a future ESP32 HTTP endpoint: GET /api/sensors */
export interface Esp32SensorReading {
  id: string
  row: number
  column: number
  moisture: number | null
  timestamp: string | null
  status: SensorStatus | 'valid' | 'stale' | 'uncalibrated' | 'invalid_low' | 'invalid_high'
  temperature?: number | null
  humidity?: number | null
}
export interface Esp32SensorsResponse { sensors: Esp32SensorReading[] }
export interface BackendCommand { id: string; created_at: string; row: number; column_number: number; valve: string; status: string; duration_ms: number; error: string | null }

/** Contract for a future POST /api/actuators/irrigate request. */
export interface IrrigationCommand { patch: { row: number; column: number }; action: 'IRRIGATE'; requestedVolumeMl?: number }
export interface HardwareConnectionStatus { esp32: 'connected' | 'disconnected'; sensorsActive: number; actuator: 'ready' | 'unavailable' }

/** Shared provider boundary; UI can expose status without knowing its source. */
export interface SensorProviderContract { readonly source: 'simulation' | 'hardware'; getStatus(): HardwareConnectionStatus }

export interface ESP32SensorProvider extends SensorProviderContract {
  readonly source: 'hardware'
  getStatus(): HardwareConnectionStatus
  getSensorEndpoint(): string
  getActuatorEndpoint(): string
  readSensors(): Promise<Esp32SensorsResponse>
}

/**
 * Frontend-safe adapter boundary. It deliberately makes no network call until
 * a future firmware/base URL integration supplies a real transport.
 */
export class ESP32HttpSensorProvider implements ESP32SensorProvider {
  readonly source = 'hardware' as const
  private status: HardwareConnectionStatus = { esp32: 'disconnected', sensorsActive: 0, actuator: 'unavailable' }
  private readonly baseUrl = import.meta.env.VITE_FARM_API_URL ?? 'http://localhost:8000'
  getStatus(): HardwareConnectionStatus { return this.status }
  getSensorEndpoint() { return '/api/sensors' }
  getActuatorEndpoint() { return '/api/actuators/irrigate' }
  async readSensors(): Promise<Esp32SensorsResponse> {
    const response = await fetch(`${this.baseUrl}${this.getSensorEndpoint()}`)
    if (!response.ok) throw new Error(`Backend sensor request failed (${response.status}).`)
    const result = await response.json() as Esp32SensorsResponse
    const sensorsActive = result.sensors.filter((sensor) => sensor.status === 'active' || sensor.status === 'valid').length
    this.status = { esp32: 'connected', sensorsActive, actuator: 'ready' }
    return result
  }
  async irrigate(command: IrrigationCommand): Promise<{ command_id: string; duration_ms: number }> {
    const response = await fetch(`${this.baseUrl}${this.getActuatorEndpoint()}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(command) })
    if (!response.ok) { const body = await response.json().catch(() => null) as { detail?: string } | null; throw new Error(body?.detail ?? `Irrigation request failed (${response.status}).`) }
    return response.json() as Promise<{ command_id: string; duration_ms: number }>
  }
  async readCommandHistory(): Promise<BackendCommand[]> {
    const response = await fetch(`${this.baseUrl}/api/commands/history`)
    if (!response.ok) throw new Error(`Backend command history request failed (${response.status}).`)
    return (await response.json() as { commands: BackendCommand[] }).commands
  }
}

/** Future actuator boundary. A real implementation will POST IrrigationCommand to the ESP32. */
export interface ESP32Actuator { readonly source: 'hardware'; getStatus(): HardwareConnectionStatus; irrigate(command: IrrigationCommand): Promise<void> }
