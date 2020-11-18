class Client:
    def __init__(self, current_floor, desired_floor):
        self.desired_floor = desired_floor
        self.time_in_sys = 0
        self.current_floor = current_floor
        if (current_floor <= 15 and desired_floor >= 16) or (current_floor >= 15 and desired_floor <= 16):
            self.need_swap = True
        else:
            self.need_swap = False

    def abandon(self):
        return self.time_in_sys > 15 * 60


