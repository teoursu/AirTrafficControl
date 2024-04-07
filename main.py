from uagents import Bureau, Context
from AirplaneAgent import AirplaneAgent
from ATCAgent import ATCAgent
from models import CollisionAdjustment, PositionReport

bureau = Bureau()

airplane1 = AirplaneAgent(name="airplane1", seed="airplane1_seed", coordinates=(6, 6), speed=2.0,
                          landing_position=(10, 10))
airplane2 = AirplaneAgent(name="airplane2", seed="airplane2_seed", coordinates=(8, 8), speed=1.0,
                          landing_position=(10, 10))
air_traffic_control = ATCAgent(name="air_traffic_control", landing_position=(10, 10), airplanes=[airplane1, airplane2])

bureau.add(air_traffic_control)
bureau.add(airplane1)
bureau.add(airplane2)


async def report_position_airplane(airplane, ctx: Context):
    airplane.update_position()
    await ctx.send(air_traffic_control.address, PositionReport(position=airplane.coordinates))


@airplane1.on_interval(period=5.0)
async def report_position_airplane1(ctx: Context):
    await report_position_airplane(airplane1, ctx)


@airplane2.on_interval(period=5.0)
async def report_position_airplane2(ctx: Context):
    await report_position_airplane(airplane2, ctx)


@airplane1.on_message(model=CollisionAdjustment)
async def adjust_for_collision_airplane1(self, msg: CollisionAdjustment):
    if msg.new_position:
        self.coordinates = msg.new_position


@airplane2.on_message(model=CollisionAdjustment)
async def adjust_for_collision_airplane2(self, msg: CollisionAdjustment):
    if msg.new_position:
        self.coordinates = msg.new_position


@air_traffic_control.on_message(model=PositionReport)
async def handle_position_report(ctx: Context, sender: str, msg: PositionReport):
    airplane = air_traffic_control.airplanes.get(sender)

    if airplane:
        airplane_name = airplane.name
        if msg.position == air_traffic_control.landing_position:
            await ctx.send(air_traffic_control.address,
                           CollisionAdjustment(message="Landing permission granted.", new_position=None))
            ctx.logger.info(f"Landing permission granted for {airplane_name} at position {msg.position}.")
            await air_traffic_control.mark_landed(sender)
        else:
            ctx.logger.info(f"{airplane_name} not at landing position yet. {msg.position}")
            await air_traffic_control.check_for_collisions(ctx)
    else:
        ctx.logger.info(f"{sender} is not in flying")


if __name__ == "__main__":
    bureau.run()
