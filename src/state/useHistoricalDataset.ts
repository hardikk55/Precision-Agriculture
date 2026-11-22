import { useCallback, useEffect, useMemo, useState } from 'react'
import { api, type Dataset, type HistoricalReading } from '../data/historicalApi'
import type { Farm } from '../models/farm'
import { needsIrrigation } from '../moistureScale'
const maps=[['S00',0,0],['S01',0,1],['S10',1,0],['S11',1,1]] as const
const moisture=(r:HistoricalReading)=>r.moisture_after!==null&&r.watering_status?.toLowerCase()==='watered'?r.moisture_after:r.moisture_before
export function toFarm(readings: HistoricalReading[]): Farm {
  const ordered = [...readings].sort((a, b) => a.timestamp.localeCompare(b.timestamp))
  const patches = maps.map(([sensorId, row, column]) => {
    const series = ordered.filter((r) => r.sensor_id === sensorId && moisture(r) !== null)
    const last = series.at(-1); const value = last ? moisture(last)! : Number.NaN
    return { id: `patch-${row}-${column}`, row, column, sensorId, soilMoisture: value, actualMoisture: value, temperature: last?.temperature ?? Number.NaN, humidity: last?.humidity ?? Number.NaN, irrigationRequired: needsIrrigation(value), irrigationStatus: 'idle' as const, lastIrrigated: null, lastIrrigatedAt: null, cumulativeWaterUsed: 0, dataSource: 'measured' as const, history: series.map((r) => ({ time: new Date(r.timestamp).toLocaleString(), moisture: moisture(r)!, irrigated: r.watering_status?.toLowerCase() === 'watered' })) }
  })
  const sensors = maps.map(([id, row, column]) => {
    const last = ordered.filter((r) => r.sensor_id === id && moisture(r) !== null).at(-1)
    return { id, type: 'Capacitive Soil Moisture' as const, row, column, currentReading: last ? moisture(last)! : Number.NaN, lastReading: last ? new Date(last.timestamp).toLocaleString() : 'No recorded data', lastSampleAt: last ? new Date(last.timestamp).getTime() : 0, status: last ? 'active' as const : 'offline' as const, dataSource: 'measured' as const }
  })
  return { patches, sensors, irrigationHistory: [] }
}
export function useHistoricalDataset(){const [datasets,setDatasets]=useState<Dataset[]>([]);const [activeId,setActiveId]=useState<string|null>(null);const [records,setRecords]=useState<HistoricalReading[]>([]);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const load=useCallback(async(id?:string)=>{setLoading(true);setError('');try{const listed=await api.datasets();setDatasets(listed.datasets);const target=id??listed.datasets.find(d=>d.active)?.id??listed.datasets.find(d=>d.source_kind==='seed')?.id;if(!target)throw Error('No historical dataset is available.');setActiveId(target);setRecords((await api.readings(target)).readings)}catch(e){setRecords([]);setError(e instanceof Error?e.message:'Could not load historical data.')}finally{setLoading(false)}},[]);useEffect(()=>{void load()},[load]);const select=useCallback(async(id:string)=>{await api.activate(id);await load(id)},[load]);return {datasets,activeId,records,farm:useMemo(()=>toFarm(records),[records]),loading,error,reload:load,select}}
