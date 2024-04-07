import collections

from uagents import Agent, Context

from models import PositionReport


async def adjust_airplane_direction(ctx: Context, airplane, index):
    airplane.speed *= (index + 0.5) / 2
    ctx.logger.info(f"Collision detected. Adjusting direction for {airplane.name}.")


class ATCAgent(Agent):
    def __init__(self, name, landing_position, airplanes):
        super().__init__(name=name)
        self.landing_position = landing_position
        self.airplanes = {}
        self.name_to_id = {}
        self.landed_airplanes = set()
        for airplane in airplanes:
            self.add_airplane(airplane)

    def add_airplane(self, airplane):
        self.name_to_id[airplane.name] = airplane.address
        self.airplanes[airplane.address] = airplane

    def mark_landed(self, airplane_id):
        if airplane_id in self.airplanes:
            airplane = self.airplanes[airplane_id]
            airplane.has_landed = True
            self.landed_airplanes.add(airplane_id)
            del self.airplanes[airplane_id]

    async def handle_position_report(self, ctx: Context, sender: str, msg: PositionReport):
        airplane = self.airplanes[sender]
        if msg.position == self.landing_position and not airplane.has_landed:
            ctx.logger.info(f"Landing permission granted for {sender} at position {msg.position}.")
            await self.mark_landed(sender)
        else:
            ctx.logger.info(f"{sender} not at landing position yet. {msg.position}")
            await self.check_for_collisions(ctx)

    async def check_for_collisions(self, ctx: Context):
        future_positions = self.calculate_future_positions()
        positions_count = collections.Counter(future_positions.values())
        for position, count in positions_count.items():
            if count > 1:
                airplanes_at_position = [airplane_id for airplane_id, future_position in future_positions.items()
                                         if future_position == position]
                for index, airplane_id in enumerate(airplanes_at_position):
                    await adjust_airplane_direction(ctx, self.airplanes[airplane_id], index)

    def calculate_future_positions(self):
        future_positions = {}
        for airplane_id, airplane in self.airplanes.items():
            if not airplane.has_landed:
                x, y = airplane.coordinates
                future_x = min(self.landing_position[0], x + airplane.speed)
                future_y = min(self.landing_position[1], y + airplane.speed)
                future_positions[airplane_id] = (future_x, future_y)
        return future_positions
