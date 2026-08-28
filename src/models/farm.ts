export type DataSource = 'simulated' | 'measured' | 'estimated'
export type IrrigationStatus = 'idle' | 'irrigating'

export interface Patch {
  id: string
  row: number
  column: number
  soilMoisture: number
  temperature: number
  humidity: number
  irrigationRequired: boolean
  irrigationStatus: IrrigationStatus
  lastIrrigated: string | null
  cumulativeWaterUsed: number
  dataSource: DataSource
}

export interface Farm { patches: Patch[] }
export interface FarmEvent { id: string; time: string; message: string; kind: 'system' | 'warning' | 'action' }

export const farmConfig = {
  moistureThreshold: 30,
  evaporationRate: 0.42,
  irrigationEffect: 18,
  irrigationWaterLitres: 1.5,
  simulationStepMinutes: 5,
} as const

const seed = [
  [55, 26.4, 71], [42, 29.1, 62], [61, 24.8, 78],
  [35, 31.6, 53], [18, 33.4, 45], [48, 27.7, 66],
  [57, 25.5, 75], [31, 30.2, 58], [22, 34.1, 41],
]

export function createInitialFarm(): Farm {
  return {
    patches: seed.map(([soilMoisture, temperature, humidity], index) => ({
      id: `patch-${Math.floor(index / 3)}-${index % 3}`,
      row: Math.floor(index / 3), column: index % 3, soilMoisture, temperature, humidity,
      irrigationRequired: soilMoisture < farmConfig.moistureThreshold,
      irrigationStatus: 'idle', lastIrrigated: null, cumulativeWaterUsed: 0, dataSource: 'simulated',
    })),
  }
}
