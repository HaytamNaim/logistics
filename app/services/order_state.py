"""Order status state machine: DRAFT -> CONFIRMED -> PREPARING -> READY_FOR_PICKUP | CANCELLED."""
ORDER_STATUS_FLOW = {
    "DRAFT": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["READY_FOR_PICKUP", "CANCELLED"],
    "READY_FOR_PICKUP": [],  # terminal for order; delivery takes over
    "CANCELLED": [],
}


def can_transition(current: str, to_status: str) -> bool:
    allowed = ORDER_STATUS_FLOW.get(current, [])
    return to_status in allowed
