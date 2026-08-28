import type { Patch } from '../models/farm'

export interface SensorProvider { advance(patch: Patch, step: number): Patch }

export class SimulatedSensorProvider implements SensorProvider {
  constructor(private readonly evaporationRate: number) {}
  advance(patch: Patch, step: number): Patch {
    const drift = (((patch.row * 7 + patch.column * 5 + step * 3) % 9) - 4) / 10
    return {
      ...patch,
      soilMoisture: Number(Math.max(0, patch.soilMoisture - this.evaporationRate + drift / 8).toFixed(1)),
      temperature: Number(Math.min(40, Math.max(20, patch.temperature + drift / 3)).toFixed(1)),
      humidity: Number(Math.min(90, Math.max(30, patch.humidity - drift / 2)).toFixed(1)),
    }
  }
}
