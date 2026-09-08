class RuleBasedDecisionEngine:
    def __init__(self, threshold_percent: float): self.threshold_percent = threshold_percent
    def requires_irrigation(self, moisture_percent: float | None) -> bool:
        return moisture_percent is not None and moisture_percent < self.threshold_percent
