import type { Farm, FarmEvent, Patch } from '../models/farm'
import type { DecisionEngine } from '../decision/RuleBasedDecisionEngine'

export interface PatchActuator { irrigatePatch(farm: Farm, row: number, column: number, simulationTime: Date): { farm: Farm; events: FarmEvent[] } }

export class VirtualSolenoidActuator implements PatchActuator {
  constructor(private readonly engine: DecisionEngine, private readonly effect: number, private readonly waterLitres: number) {}
  irrigatePatch(farm: Farm, row: number, column: number, time: Date) {
    const patch = farm.patches.find((item) => item.row === row && item.column === column)
    if (!patch) return { farm, events: [] }
    const label = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); const before = patch.actualMoisture
    const completed: Patch = { ...patch, irrigationStatus: 'idle', actualMoisture: Math.min(5, Number((before + this.effect).toFixed(1))), cumulativeWaterUsed: Number((patch.cumulativeWaterUsed + this.waterLitres).toFixed(1)), lastIrrigated: label, lastIrrigatedAt: time.getTime() }
    completed.irrigationRequired = this.engine.requiresIrrigation(completed)
    const events: FarmEvent[] = [
      { id: crypto.randomUUID(), time: label, kind: 'action', message: `Irrigation requested for Pot (${row},${column}).` },
      { id: crypto.randomUUID(), time: label, kind: 'action', message: 'Virtual solenoid activated.' },
      { id: crypto.randomUUID(), time: label, kind: 'action', message: `Irrigation completed: soil moisture score ${before}/5 → ${completed.actualMoisture}/5.` }
    ]
    return { farm: { ...farm, patches: farm.patches.map((item) => item.id === patch.id ? completed : item) }, events }
  }
}
