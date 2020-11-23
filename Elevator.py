import numpy as np
import random
import heapq as hpq


class Elevator:
    def __init__(self, number, saturday):
        self.number = number
        self.floor = 0
        self.capacity = 0
        self.is_stuck = False
        self.clients = []  # client in elevator
        self.saturday = saturday  # defines saturday elevator behaviour
        self.up_queue = []
        self.down_queue = []  # push floors to queue with *-1 to maintain hpq pulling the max element, Simulation pushes
        self.doors_open = False
        self.up = True
        self.orders = set()  # keeps track of orders being made

        if self.number <= 2:  # elevators 1,2
            self.service_floors = set([i for i in range(16)])
        elif self.number > 2:  # elevators 3,4
            self.service_floors = set([i for i in range(16, 26)])
            self.service_floors.add(0)

    def __repr__(self):
        return "Elevator {}, {} clients at floor {}".format(self.number, self.capacity, self.floor)

    def stuck(self):
        """
        method to randomize Elevator getting stuck
        :return: boolean
        """
        if random.random(1) <= 0.0005:
            self.is_stuck = True
            return True
        return False

    def fix_elevator(self):
        self.is_stuck = False

    def add_to_queue(self, floor, direction):
        if abs(floor) not in self.orders:  # avoid negative numbers, use abs()
            if direction == "up":
                self.up_queue.append(floor)
            else:
                self.down_queue.append(floor)
            self.orders.add(abs(floor))  # add to set

    def is_full(self):
        """
        check if Elevator is full or not
        :return:
        """
        return self.capacity == 15

    def free_space(self):
        """
        calculate how many clients can board the Elevator
        :return: int
        """
        return 15 - self.capacity

    def remove_clients(self, clients_lst):
        self.doors_open = True
        for client in clients_lst:
            client.travelling = False
            self.clients.remove(client)
        self.capacity -= len(clients_lst)

    def board_clients(self, clients_lst):
        self.clients += clients_lst
        self.capacity += len(clients_lst)
        self.doors_open = False

    def travel(self):
        """
        pop floor out of queue, move elevator, flip elevator direction if necessary
        :return: time of travel between floors
        """
        if self.saturday:
            # change elevator direction on end of range
            if (self.up and self.floor in (15, 25)) or (not self.up and self.floor == 0):
                self.up = not self.up
            if self.up:
                self.floor += 1
                travel_time = 5
            elif not self.up and self.floor != 16:  # go down from 16 to 0
                self.floor -= 1
                travel_time = 5
            else:
                self.floor = 0
                travel_time = 20  # travel from 16 to 0
        else:
            if self.up:
                next_floor = hpq.heappop(self.up_queue)

            else:
                next_floor = hpq.heappop(self.down_queue) * (-1)  # gets minimum
                self.orders.remove(next_floor)
            self.floor = next_floor  # move elevator
            # top or bottom floor, or only 1 of the queues are empty
            if next_floor in (0, 16, 25) or (bool(self.up_queue) != bool(self.down_queue)):
                self.up = not self.up  # flip elevator direction
            travel_time = 4 + abs(self.floor - next_floor)
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
    print(bool([1,23]),bool([]))
    pass
