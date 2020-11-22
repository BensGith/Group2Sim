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

    def update_client_time(self, time):
        for client in self.clients:
            client.add_wait_time(time)

    def drop_clients(self, elevator):
        """
        method to drop clients in matching floor
        :param elevator: Elevator object
        :return: None
        """
        dropped = 0
        leaving = []
        for client in elevator.clients:
            if self.number == client.desired_floor:  # client reached desired floor
                leaving.append(client)
                dropped += 1

            elif elevator.saturday and client.desired_floor not in elevator.next_floors and self.number == 0:
                hpq.heappush(self.line, client)  # add client to queue
                leaving.append(client)
        elevator.remove_clients(leaving)  # remove from system
        return dropped

    def board_clients(self, elevator):
        """
        remove n<= free space in elevator of people from line if they need this elevator
        :return: None
        """
        boarding = []
        staying = []

        while self.line or len(boarding) == elevator.free_space():  # stop boarding people if line is empty or 15 inside
            client = hpq.heappop(self.line)
            # on saturday mode, client will board ANY elevator
            if elevator.saturday:  # need swap
                boarding.append(client)
                self.n_clients -= 1  # update number of staying in the floor
            elif client.desired_floor in elevator.next_floors:  # also for swap on 15th floor
                boarding.append(client)
                self.n_clients -= 1  # update number of staying in the floor
            else:
                staying.append(client)
        if staying:
            for client in staying:
                hpq.heappush(self.line, client)  # push clients back to line
        elevator.board_clients(boarding)  # board clients to elevator


if __name__ == "__main__":
    # test adding and removing from elevator
    pass
