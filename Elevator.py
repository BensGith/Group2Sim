import numpy as np
import heapq as hpq


class Elevator:
    def __init__(self, number, saturday):
        self.number = number
        self.capacity = 0
        self.is_stuck = False
        self.clients = []  # client in elevator
        self.saturday = saturday  # defines saturday elevator behaviour
        self.up_queue = []
        self.down_queue = []  # push floors to queue with *-1 to maintain hpq pulling the max element, Simulation pushes
        self.doors_open = False
        self.up = True
        self.start = False  # flag if elevator was called yet or not
        if self.saturday:  # start elevator at random floor on saturday
            if self.number <= 2:  # for elevators 1,2 start from 0 - 15
                self.floor = np.random.choice([i for i in range(16)], 1)[0]  # returns a list, take arg 0
            else:  # for elevators 3,4 start from 0 or 16-25
                self.floor = np.random.choice([0] + [i for i in range(16, 25)], 1)[0]  # returns a list, take arg 0
        else:
            self.floor = 0
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
        if np.random.random(1) <= 0.0005:
            self.is_stuck = True
            print(str(self.number) + 'is_stuck')
            return True
        return False

    def fix_elevator(self):
        self.is_stuck = False

    def add_to_queue(self, floors, direction):

        source_floor = floors[0]
        target_floor = floors[1]
        if source_floor not in self.orders and source_floor != self.floor:  # avoid negative numbers, use abs()
            if source_floor > self.floor:
                hpq.heappush(self.up_queue, source_floor)
            else:
                hpq.heappush(self.down_queue, source_floor*-1)
            self.orders.add(abs(source_floor))  # add to set
        if target_floor not in self.orders:
            if direction == "up":
                hpq.heappush(self.up_queue, target_floor)
            else:
                hpq.heappush(self.down_queue, target_floor*-1)
            self.orders.add(abs(target_floor))

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
            client.floor_time = 0
            client.current_floor = self.floor  # update client's current floor
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
            if self.up and self.up_queue:  # move elevator to next floor from queue
                next_floor = hpq.heappop(self.up_queue)
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
            elif not self.up and self.down_queue:  # move elevator to next floor from queue
                next_floor = hpq.heappop(self.down_queue) * (-1)  # gets minimum
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
            elif self.up and not self.up_queue and self.down_queue:
                next_floor = hpq.heappop(self.down_queue) * (-1)  # gets minimum
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
                self.up = False
            elif not self.up and not self.down_queue and self.up_queue:
                next_floor = hpq.heappop(self.up_queue)
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
            elif self.up_queue:
                next_floor = hpq.heappop(self.up_queue)
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
                self.up = True
            elif self.down_queue:
                next_floor = hpq.heappop(self.down_queue) *(-1)
                self.orders.remove(next_floor)
                travel_time = 4 + abs(self.floor - next_floor)
                self.up = False

            else:
                next_floor = 0
                travel_time = abs(self.floor - next_floor)
            self.floor = next_floor  # move elevator
            # top or bottom floor, or only 1 of the queues are empty
            if next_floor in (0, 16, 25) or (not self.up_queue and self.up) or (not self.down_queue and not self.up):
                self.up = not self.up  # flip elevator direction
        for client in self.clients:
            client.travel()
        return travel_time

    def press_button(self, floor, direction):
        """
        client will press this button to add floor to queue when the doors are open at his floor
        :return: None
        """
        self.orders.add(floor)
        if direction == "up":
            self.up_queue.append(floor)

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
