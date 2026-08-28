import { useCallback, useEffect, useMemo, useState } from 'react'
import { VirtualSolenoidActuator } from '../actuation/VirtualSolenoidActuator'
import { RuleBasedDecisionEngine } from '../decision/RuleBasedDecisionEngine'
import { createInitialFarm, farmConfig, type Farm, type FarmEvent } from '../models/farm'
import { SimulatedSensorProvider } from '../simulation/SensorSimulator'

const initialTime = new Date('2026-08-28T08:00:00')
const makeEvent = (message: string, kind: FarmEvent['kind'] = 'system', time = initialTime) => ({ id: crypto.randomUUID(), time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), message, kind })

export function useFarmSimulation() {
  const engine = useMemo(() => new RuleBasedDecisionEngine(farmConfig.moistureThreshold), [])
  const sensors = useMemo(() => new SimulatedSensorProvider(farmConfig.evaporationRate), [])
  const actuator = useMemo(() => new VirtualSolenoidActuator(engine, farmConfig.irrigationEffect, farmConfig.irrigationWaterLitres), [engine])
  const [farm, setFarm] = useState<Farm>(createInitialFarm)
  const [running, setRunning] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [step, setStep] = useState(0)
  const [simulationTime, setSimulationTime] = useState(initialTime)
  const [events, setEvents] = useState<FarmEvent[]>([makeEvent('Digital farm initialized with simulated sensor data.')])

  const advance = useCallback(() => {
    setStep((previous) => previous + 1)
    setSimulationTime((previous) => new Date(previous.getTime() + farmConfig.simulationStepMinutes * 60_000))
    setFarm((previous) => {
      const patches = previous.patches.map((patch) => {
        const next = sensors.advance(patch, step + 1)
        return { ...next, irrigationRequired: engine.requiresIrrigation(next) }
      })
      const newlyDry = patches.filter((patch, i) => patch.irrigationRequired && !previous.patches[i].irrigationRequired)
      if (newlyDry.length) setEvents((log) => [...newlyDry.map((patch) => makeEvent(`Patch (${patch.row},${patch.column}) moisture dropped below threshold.`, 'warning', new Date(simulationTime.getTime() + farmConfig.simulationStepMinutes * 60_000))), ...log].slice(0, 40))
      return { patches }
    })
  }, [engine, sensors, simulationTime, step])

  useEffect(() => { if (!running) return; const timer = window.setInterval(advance, 1600 / speed); return () => window.clearInterval(timer) }, [advance, running, speed])
  const irrigate = (row: number, column: number) => {
    const target = farm.patches.find((patch) => patch.row === row && patch.column === column)
    if (!target || target.irrigationStatus === 'irrigating') return
    setFarm((previous) => ({ patches: previous.patches.map((patch) => patch.row === row && patch.column === column ? { ...patch, irrigationStatus: 'irrigating' } : patch) }))
    setEvents((log) => [makeEvent(`Virtual solenoid activated for Patch (${row},${column}).`, 'action', simulationTime), makeEvent(`Irrigation requested for Patch (${row},${column}).`, 'action', simulationTime), ...log].slice(0, 40))
    window.setTimeout(() => {
      setFarm((previous) => {
        const result = actuator.irrigatePatch(previous, row, column, simulationTime)
        setEvents((log) => [result.events[2], ...log].slice(0, 40))
        return result.farm
      })
    }, 650)
  }
  const reset = () => { setFarm(createInitialFarm()); setRunning(false); setStep(0); setSimulationTime(initialTime); setEvents([makeEvent('Simulation reset to initial simulated farm state.')]) }
  return { farm, running, setRunning, speed, setSpeed, simulationTime, events, irrigate, reset }
}
