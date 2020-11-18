import heapq as hpq


class Floor:
    def __init__(self, number):
        self.clients = []
        self.number = number
        self.line = []  # priority queue
        self.n_clients = 0

    def __repr__(self):
        return "Floor: {}".format(self.number)

    def add_to_line(self, client):
        hpq.heappush(self.line, client)
        self.n_clients += 1

    def remove_from_line(self, elevator):
        """
        remove n<= free space in elevator of people from line if they need this elevator
        :return:
        """
        boarding = []
        staying = []

        while self.line or boarding == 15 - elevator.capacity:  # stop boarding people if line is empty or 15 inside
            client = hpq.heappop(self.line)
            if self.number == 15:
                pass

            if client.desired_floor in elevator.next_floors or elevator.saturday:
                boarding.append(client)
                self.n_clients -= 1  # update number of staying in the floor
            else:
                staying.append(client)
        if staying:
            for client in staying:
                hpq.heappush(self.line, client)  # push clients back to line
        return boarding












