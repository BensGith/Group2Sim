class Client:
    def __init__(self, current_floor, desired_floor, arrival_time):
        self.arrival_time = arrival_time
        self.desired_floor = desired_floor
        self.time_in_sys = 0  # client's overall time in the system
        self.floor_time = 0  # client's floor time
        self.travelling = False  # set flag if client is moving the elevator
        self.current_floor = current_floor  # client's current floor
        self.direction = None  # direction the client wants to go up/down
        self.got_service = False  # flag to track if client ever boarded an elevator
        self.reorder = False # if client switched elevator, value will be true
        if (1 <= current_floor <= 15 and desired_floor >= 16) or (current_floor >= 16 and desired_floor <= 15 and desired_floor != 0):
            self.need_swap = True  # use for ordering elevators in Simulation
        else:
            self.need_swap = False  # use for ordering elevators in Simulation (will order it to go to 0)
        if not self.need_swap:
            if self.current_floor < self.desired_floor:
                self.direction = True
            elif self.current_floor > self.desired_floor:
                self.direction = False
        else:  # need swap, take any elevator going down
            self.direction = False

    def __repr__(self):
        return "Client's arrival time is {}, current floor {}, desired floor {}, and need swap? {}".format(
                                            self.arrival_time, self.current_floor, self.desired_floor, self.need_swap)

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

    def add_wait_time(self, time):
        self.floor_time += time

    def add_system_time(self, time):
        self.time_in_sys += time

    def travel(self):
        self.travelling = True
        self.floor_time = 0  # push client to end of line
