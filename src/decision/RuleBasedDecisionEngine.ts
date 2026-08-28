import type { Patch } from '../models/farm'

export interface DecisionEngine { requiresIrrigation(patch: Patch): boolean }

export class RuleBasedDecisionEngine implements DecisionEngine {
  constructor(private readonly moistureThreshold: number) {}
  requiresIrrigation(patch: Patch): boolean { return patch.soilMoisture < this.moistureThreshold }
}
