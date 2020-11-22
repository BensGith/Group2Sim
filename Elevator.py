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

        if not self.saturday and self.number <= 2:  # elevators 1,2
            self.next_floors = set([i for i in range(16)])
        elif not self.saturday and self.number > 2:
            self.next_floors = set([i for i in range(16, 26)])  # elevators 3,4
            self.next_floors.add(0)
        else:
            self.next_floors = set()

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
        if direction == "up":
            self.up_queue.append(floor)
        else:
            self.down_queue.append(floor)

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
            self.clients.remove(client)
        self.capacity -= len(clients_lst)

    def remove_floor_fq(self, floor, direction):
        """
        when the elevator closes its doors, pull the next floor and remove it from queue and set
        :param floor:
        :param direction:
        :return:
        """
        pass

    def board_clients(self, clients_lst):
        self.clients += clients_lst
        self.capacity += len(clients_lst)
        self.doors_open = False

    def update_clients_time(self):
        travel_time = self.ride_time()
        for client in self.clients:
            client.add_travel_time(travel_time)  # add client travel time between floors

    def ride_time(self):
        """
        pop floor out of queue, move elevator
        :return: time of travel between floors
        """
        if self.up:
            next_floor = hpq.heappop(self.up_queue)
        else:
            next_floor = hpq.heappop(self.down_queue) * (-1)  # gets minimum
        self.floor = next_floor  # move elevator
        return 4 + abs(self.floor - next_floor)

    @staticmethod
    def get_fix_time():
        """
        randomize time for elevator to be fixed
        :return: time of fix in seconds
        """
        return np.random.uniform(5 * 60, 15 * 60)
