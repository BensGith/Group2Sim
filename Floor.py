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
        :return: None
        """
        boarding = []
        staying = []

        while self.line or boarding == elevator.free_space():  # stop boarding people if line is empty or 15 inside
            client = hpq.heappop(self.line)
            # on saturday mode, client will board ANY elevator if it's not on the 15th floor
            if client.desired_floor not in elevator.next_floors and elevator.saturday and self.number != 15:
                boarding.append(client)
                self.n_clients -= 1  # update number of staying in the floor
            elif client.desired_floor in elevator.next_floors:
                boarding.append(client)
                self.n_clients -= 1  # update number of staying in the floor
            else:
                staying.append(client)
        if staying:
            for client in staying:
                hpq.heappush(self.line, client)  # push clients back to line
        elevator.board_clients(boarding)  # board clients to elevator

    def drop_clients(self, elevator):
        """
        method to drop clients in matching floor
        :param elevator: Elevator object
        :return: None
        """
        for client in elevator.clients:
            if self.number == client.desired_floor:  # client reached desired floor
                elevator.remove_client(client)  # remove from system

            elif elevator.saturday and client.desired_floor not in elevator.next_floors and self.number == 15:
                hpq.heappush(self.line, client)  # add client to queue
                elevator.remove_client(client)  # remove client from elevator


if __name__ == "__main__":
    # test adding and removing from elevator
    pass
