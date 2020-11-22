class Client:
    def __init__(self, current_floor, desired_floor, arrival_time):
        self.arrival_time = arrival_time
        self.desired_floor = desired_floor
        self.time_in_sys = 0
        self.floor_time = 0
        self.current_floor = current_floor
        if (current_floor <= 15 and desired_floor >= 16) or (current_floor >= 15 and desired_floor <= 16):
            self.need_swap = True
        else:
            self.need_swap = False

    def __repr__(self):
        return "Client system time {}, floor time {}".format(self.time_in_sys, self.floor_time)

    def __lt__(self, other):
        return self.floor_time < other.floor_time

    def abandon(self):
        return self.time_in_sys > 15 * 60  # abandon if waiting more than 15 minutes

    def add_wait_time(self, time):
        self.time_in_sys += time
        self.floor_time += time

    def travel(self, time):
        """
        call this method when client travels in the Elevator
        :return: None
        """
        self.time_in_sys += time
        self.floor_time = 0


if __name__ == "__main__":
    lst1 = [Client(0, 1), Client(0, 2)]
    c = lst1[0]
    lst1.remove(c)
    lst2 =[]
    lst2.append(c)
    print(lst1)
    print(lst2)
