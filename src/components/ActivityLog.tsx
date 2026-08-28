import type { FarmEvent } from '../models/farm'

export function ActivityLog({ events }: { events: FarmEvent[] }) { return <section className="activity"><div className="section-heading"><div><p className="eyebrow">SYSTEM TRACE</p><h2>Activity log</h2></div><span className="live-dot">Live events</span></div><div className="events">{events.map((event) => <div className={`event ${event.kind}`} key={event.id}><time>{event.time}</time><span>{event.message}</span></div>)}</div></section> }
