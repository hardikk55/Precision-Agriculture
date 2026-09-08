from dataclasses import dataclass


@dataclass(frozen=True)
class PatchMapping:
    row: int
    column: int
    sensor_id: str
    valve: str
    valve_gpio: int
    mux_channel: str


PATCHES = tuple(PatchMapping(row, column, f"S{row}{column}", f"V{row * 3 + column + 1}", gpio, f"C{row * 3 + column}") for row, column, gpio in (
    (0, 0, 13), (0, 1, 14), (0, 2, 16), (1, 0, 17), (1, 1, 18), (1, 2, 19), (2, 0, 23), (2, 1, 25), (2, 2, 26),
))
BY_SENSOR = {item.sensor_id: item for item in PATCHES}
BY_PATCH = {(item.row, item.column): item for item in PATCHES}
PUMP_GPIO = 27
