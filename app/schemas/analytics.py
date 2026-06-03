from typing import Any
from pydantic import BaseModel


class KPIsResponse(BaseModel):
    delivery_speed_avg_mins: float | None
    delay_rate: float | None
    driver_utilization: float | None
    dimensions: dict[str, Any] | None = None  # date, zone, driver filters used
