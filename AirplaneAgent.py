from uagents import Agent


class AirplaneAgent(Agent):
    def __init__(self, name, seed, coordinates, speed, landing_position):
        super().__init__(name=name, seed=seed)
        self.coordinates = coordinates
        self.speed = speed
        self.landing_position = landing_position
        self.has_landed = False

    def update_position(self):
        if not self.has_landed:
            x, y = self.coordinates
            new_x = min(self.landing_position[0], x + self.speed)
            new_y = min(self.landing_position[1], y + self.speed)
            self.coordinates = (new_x, new_y)
