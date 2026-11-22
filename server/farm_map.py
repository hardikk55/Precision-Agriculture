from dataclasses import dataclass


@dataclass(frozen=True)
class PatchMapping:
    row: int
    column: int
    sensor_id: str
    valve: str
    pot: int


# GPIO/MUX values are intentionally absent: no verified wiring specification was supplied.
PATCHES = (
    PatchMapping(0, 0, 'S00', 'V1', 1), PatchMapping(0, 1, 'S01', 'V2', 2),
    PatchMapping(1, 0, 'S10', 'V3', 3), PatchMapping(1, 1, 'S11', 'V4', 4),
)
BY_SENSOR = {item.sensor_id: item for item in PATCHES}
BY_PATCH = {(item.row, item.column): item for item in PATCHES}
