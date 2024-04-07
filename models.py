from typing import Optional

from uagents import Model


class PositionReport(Model):
    position: tuple


class CollisionAdjustment(Model):
    message: str = ""
    new_position: Optional[tuple] = None
