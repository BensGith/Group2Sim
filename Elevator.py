import numpy as np
import random


class Elevator:
    def __init__(self, number, saturday=False):
        self.number = number
        self.floor = 0
        self.capacity = 0
        self.is_stuck = False
        self.clients = []  # client in elevator
        self.saturday = saturday  # defines saturday elevator behaviour

        if not self.saturday and self.number <= 2:  # elevators 1,2
            self.next_floors = set([i for i in range(16)])
        elif not self.saturday and self.number > 2:
            self.next_floors = set([i for i in range(16, 26)])  # elevators 3,4
            self.next_floors.add(0)
        else:
            self.next_floors = set()

    def __repr__(self):
        return "Elevator {}, {} clients at floor {}" .format(self.number, self.capacity, self.floor)

    def stuck(self):
        """
        method to randomize Elevator getting stuck
        :return:
        """
        if random.random(1) <= 0.0005:
            self.is_stuck = True
            return True

    def fix_elevator(self):
        self.is_stuck = False

    def is_full(self):
        """
        check if Elevator is full or not
        :return:
        """
        return self.capacity == 15

    def board_clients(self):
        """
        calculate how many clients can board the Elevator
        :return: int
        """
        return len(self.clients) - self.capacity

    @staticmethod
    def ride_time(floor1, floor2):
        return 4 + abs(floor1 - floor2)

    @staticmethod
    def get_fix_time():
        """
        randomize time for elevator to be fixed
        :return: time of fix in seconds
        """
        return np.random.uniform(5 * 60, 15 * 60)