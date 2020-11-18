class Client:
    def __init__(self, desired_floor):
        self.desired_floor = desired_floor
        self.time_in_sys = 0

    def abandon(self):
        return self.time_in_sys > 15 * 60

    def is_angry(self):
        return True


