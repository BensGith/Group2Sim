import numpy as np


class Elevator:
    def __init__(self, number, saturday):
        self.number = number
        self.is_stuck = False
        self.clients = []  # client in elevator
        self.saturday = saturday  # defines saturday elevator behaviour
        self.up_set = set()
        self.down_set = set()
        self.orders_up = set()  # will hold orders for next round
        self.orders_down = set()  # will hold orders for next round
        self.doors_open = False
        self.up = True
        self.start = False  # flag if elevator was called yet or not
        self.prv_open_time = 21600
        if self.saturday:  # start elevator at random floor on saturday
            if self.number <= 2:  # for elevators 1,2 start from 0 - 15
                self.floor = np.random.choice([i for i in range(16)], 1)[0]  # returns a list, take arg 0
            else:  # for elevators 3,4 start from 0 or 16-25
                self.floor = np.random.choice([0] + [i for i in range(16, 25)], 1)[0]  # returns a list, take arg 0
        else:
            self.floor = 0

        if self.number <= 2:  # elevators 1,2
            self.service_floors = set([i for i in range(16)])
        elif self.number > 2:  # elevators 3,4
            self.service_floors = set([i for i in range(16, 26)])
            self.service_floors.add(0)

    def __repr__(self):
        return "Elevator {}, {} clients at floor {}".format(self.number, len(self.clients), self.floor)

    def stuck(self):
        """
        method to randomize Elevator getting stuck
        :return: boolean
        """
        if np.random.random(1) <= 0.0005:
            self.is_stuck = True
            print(str(self.number) + ' is stuck')
            return True
        return False

    def fix_elevator(self):
        self.is_stuck = False

    def add_to_queue(self, floors, direction):
        source_floor = floors[0]
        # add press button method so clients will be guaranteed to reach their dest if boarded
        # roll orders to regular queues upon cycle finish
        # target_floor = floors[1]

        # in case we passed client, get him the next round
        if source_floor < self.floor and self.up and direction == "up":
            self.orders_up.add(source_floor)
        elif source_floor > self.floor and not self.up and direction == "down":
            self.orders_down.add(source_floor)
        # pick up client on the way up
        elif source_floor > self.floor and self.up and direction == "up":
            self.up_set.add(source_floor)
        # pick up client on the way down
        elif source_floor < self.floor and not self.up and direction == "down":
            self.down_set.add(source_floor)

    def free_space(self):
        """
        calculate how many clients can board the Elevator
        :return: int
        """
        return 15 - len(self.clients)

    def remove_clients(self, clients_lst):

        self.doors_open = True
        for client in clients_lst:
            client.travelling = False
            client.floor_time = 0
            client.current_floor = self.floor  # update client's current floor
            self.clients.remove(client)


    def board_clients(self, clients_lst):
        if not self.saturday:
            for client in clients_lst:
                if self.up:
                    self.up_set.add(client.desired_floor)
                else:
                    if client.desired_floor not in self.service_floors:
                        self.down_set.add(0)
                    else:
                        self.down_set.add(client.desired_floor)

        self.clients += clients_lst
        self.doors_open = False

    def travel(self):
        """
        pop floor out of queue, move elevator, flip elevator direction if necessary
        :return: time of travel between floors
        """
        if self.saturday:
            # change elevator direction on end of range

            if self.up and self.floor == 0 and self.number in (3, 4):  # travel from 0 to 16
                self.floor = 16
                travel_time = 20

            elif not self.up and self.floor == 16:  # go down from 16 to 0
                self.floor = 0
                travel_time = 20  # travel from 16 to 0

            elif self.up:  # moving up 1 floor
                self.floor += 1
                travel_time = 5

            else:  # moving down 1 floor
                self.floor -= 1
                travel_time = 5

            if (self.up and self.floor in (15, 25)) or (not self.up and self.floor == 0):
                self.up = not self.up
        else:
            # move to to source floor? ele on 0, request is 5 to 3 > will be pushed to down queue
            # ele on 0, request from 0 to 16
            # ele on 0, request from 0 to 5
            # ele on 0, request from 20 to 16
            # ######### RELOAD QUEUES ##############
            if not self.up_set and self.orders_up:
                self.up = self.orders_up
                self.orders_up = set()
            if not self.down_set and self.down_set:
                self.down_set = self.orders_down
                self.orders_down = set()
            if self.up and not self.up_set and not self.down_set:  # moving up, queues empty
                self.down_set = self.orders_down
                self.orders_down = set()
                self.up = False
            elif not self.up and not self.up_set and not self.down_set:
                self.up_set = self.orders_up
                self.orders_up = set()
                self.up = True
            # ###################################
            if self.floor == 0 and not self.orders_up and not self.orders_down and not self.up_set and not self.down_set:
                if self.number <= 2:
                    next_floor = 15
                    current = self.floor
                    self.floor = 15
                    for i in range(14, -1, -1):
                        self.down_set.add(i)
                else:
                    next_floor = 25
                    current = self.floor
                    self.floor = 25
                    for i in range(24, 14, -1):
                        self.down_set.add(i)
                self.up = False
                return 4+ abs(current - next_floor)

            elif self.up and self.up_set:
                next_floor = min(self.up_set)
                self.up_set.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
            elif not self.up and self.down_set:
                next_floor = max(self.down_set)
                self.down_set.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
            elif not self.up_set and not self.down_set:
                next_floor = 0
                self.up = True
                if 0 in self.orders_up:
                    self.orders_up.remove(0)
                self.up_set = self.orders_up
                self.orders_up = set()
                self.down_set = self.orders_down
                self.orders_down = set()
                travel_time = 0
            elif self.up_set:
                next_floor = min(self.up_set)
                self.up_set.remove(next_floor)
                self.up = True
                travel_time = 4 + abs(self.floor - next_floor)
            elif self.down_set:
                next_floor = max(self.down_set)
                self.down_set.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
                self.up = False
            elif self.orders_up:
                next_floor = min(self.up_set)
                self.up_set.remove(next_floor)
                self.up = True
                travel_time = 4 + abs(self.floor - next_floor)
            elif self.orders_down:
                next_floor = max(self.orders_down)
                self.orders_down.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
                self.up = False

            else:
                next_floor = 0
                self.up = True
                if 0 in self.orders_up:
                    self.orders_up.remove(0)
                travel_time = 0

            self.floor = next_floor  # move elevator
            # top or bottom floor, or only 1 of the queues are empty
            if next_floor in (15, 25) and self.up or next_floor == 0 and not self.up:
                self.up = not self.up  # flip elevator direction
        for client in self.clients:
            client.travel()
        return travel_time

    @staticmethod
    def get_fix_time():
        """
        randomize time for elevator to be fixed
        :return: time of fix in seconds
        """
        return np.random.uniform(5 * 60, 15 * 60)


if __name__ == "__main__":
    print(bool([1, 23]), bool([]))
    pass
