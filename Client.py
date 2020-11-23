class Client:
    def __init__(self, current_floor, desired_floor, arrival_time):
        self.arrival_time = arrival_time
        self.desired_floor = desired_floor
        self.time_in_sys = 0
        self.floor_time = 0
        self.travelling = False
        self.current_floor = current_floor
        self.direction = None
        if (current_floor <= 15 and desired_floor >= 16) or (current_floor >= 15 and desired_floor <= 16):
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
        return "Client system time {}, floor time {}".format(self.time_in_sys, self.floor_time)

    def __lt__(self, other):
        return self.floor_time < other.floor_time

    def abandon(self):
        # check if client inside elevator
        return self.time_in_sys > 15 * 60  # abandon if waiting more than 15 minutes

    def add_wait_time(self, time):
        self.floor_time += time

    def add_system_time(self, time):
        self.time_in_sys += time

    def travel(self):
        self.travelling = True
        self.floor_time = 0


if __name__ == "__main__":
    lst1 = [Client(0, 1), Client(0, 2)]
    c = lst1[0]
    lst1.remove(c)
    lst2 =[]
    lst2.append(c)
    print(lst1)
    print(lst2)
