"""Delivery status FSM: PREPARATION -> IN_TRANSIT -> DELIVERED | FAILED | RETURNED."""
DELIVERY_STATUS_FLOW = {
    "PREPARATION": ["IN_TRANSIT", "FAILED", "RETURNED"],
    "IN_TRANSIT": ["DELIVERED", "FAILED", "RETURNED"],
    "DELIVERED": [],
    "FAILED": [],
    "RETURNED": [],
}


def can_transition(current: str, to_status: str) -> bool:
    allowed = DELIVERY_STATUS_FLOW.get(current, [])
    return to_status in allowed
