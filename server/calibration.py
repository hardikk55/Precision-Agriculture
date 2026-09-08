def moisture_percent(raw_adc: int, adc_dry: int, adc_wet: int) -> float:
    """Maps either ADC direction to 0=dry, 100=wet and bounds the result."""
    if adc_dry == adc_wet:
        raise ValueError("ADC_DRY and ADC_WET must differ")
    value = (raw_adc - adc_dry) / (adc_wet - adc_dry) * 100
    return round(max(0.0, min(100.0, value)), 2)
