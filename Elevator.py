import numpy as np
import random


class Elevator:
    def __init__(self):
        self.floor = "floor object"
        self.capacity = 0
        self.is_stuck = False
        self.clients = []  # client in elevator

    def stuck(self):
        if random.random(1) <= 0.0005:
            self.is_stuck = True

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
