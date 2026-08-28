import type { SensorStatus } from '../models/farm'

/** Contract expected from a future ESP32 HTTP endpoint: GET /api/sensors */
export interface Esp32SensorReading {
  id: string
  row: number
  column: number
  moisture: number
  timestamp: string
  status: SensorStatus
}
export interface Esp32SensorsResponse { sensors: Esp32SensorReading[] }

/** Contract for a future POST /api/actuators/irrigate request. */
export interface IrrigationCommand { patch: { row: number; column: number }; action: 'IRRIGATE'; durationMs: number }
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
  getStatus(): HardwareConnectionStatus { return { esp32: 'disconnected', sensorsActive: 0, actuator: 'unavailable' } }
  getSensorEndpoint() { return '/api/sensors' }
  getActuatorEndpoint() { return '/api/actuators/irrigate' }
  async readSensors(): Promise<Esp32SensorsResponse> { throw new Error('ESP32 hardware is not connected.') }
}

/** Future actuator boundary. A real implementation will POST IrrigationCommand to the ESP32. */
export interface ESP32Actuator { readonly source: 'hardware'; getStatus(): HardwareConnectionStatus; irrigate(command: IrrigationCommand): Promise<void> }
