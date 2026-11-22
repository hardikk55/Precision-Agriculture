export const MOISTURE_THRESHOLD = 3
export const needsIrrigation = (score: number) => Number.isFinite(score) && score <= MOISTURE_THRESHOLD
export const scoreLabel = (score: number, digits = 1) => Number.isFinite(score) ? `${score.toFixed(digits)}/5` : '—'
export const scoreClass = (score: number) => !Number.isFinite(score) ? 'offline' : needsIrrigation(score) ? 'dry' : 'wet'
