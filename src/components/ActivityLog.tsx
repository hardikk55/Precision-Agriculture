import type { FarmEvent } from '../models/farm'

export function ActivityLog({ events }: { events: FarmEvent[] }) { return <section className="activity"><div className="section-heading"><div><p className="eyebrow">CHRONOLOGICAL SYSTEM TRACE</p><h2>Event timeline</h2></div><span className="live-dot">Latest events</span></div><div className="events">{events.map((event) => <div className={`event ${event.kind}`} key={event.id}><time>{event.time}</time><span>{event.message}</span></div>)}</div></section> }
