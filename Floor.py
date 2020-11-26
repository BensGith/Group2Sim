import heapq as hpq


class Floor:
    def __init__(self, number):
        self.number = number
        self.line = []  # priority queue
        self.n_clients = 0

    def __repr__(self):
        return "Floor: {}, Clients {}".format(self.number, self.n_clients)

    def add_to_line(self, client):
        hpq.heappush(self.line, client)
        self.n_clients += 1

    def remove_from_line(self, client):
        self.line.remove(client)
        self.n_clients -= 1


    def order_line(self):
        """
        use this method to order the line after client abandoning
        :return:
        """
        hpq.heapify(self.line)
        
    def update_client_time(self, time):
        for client in self.line:
            client.add_wait_time(time)

    def drop_clients(self, elevator, curr_time):
        """
        method to drop clients in matching floor
        :param elevator: Elevator object
        :return: None
        """
        dropped = 0
        leaving = []
        service_time = []
        for client in elevator.clients:
            if self.number == client.desired_floor:  # client reached desired floor
                client.time_in_sys = curr_time - client.arrival_time
                service_time.append(client.time_in_sys)
                leaving.append(client)
                dropped += 1
            elif client.desired_floor not in elevator.service_floors and self.number == 0:  # go off elevator for swap
                client.direction = True
                leaving.append(client)
                self.line.append(client)
                dropped += 1
        if dropped > 0:
            hpq.heapify(self.line)
            elevator.remove_clients(leaving)  # remove from system

        return service_time

    def board_clients(self, elevator, curr_time):
        """
        remove n<= free space in elevator of people from line if they need this elevator
        :return: None
        """
        boarding = []
        staying = []
        abandoned = 0

        while self.line and len(boarding) < elevator.free_space():  # stop boarding people if line is empty or 15 inside
            client = hpq.heappop(self.line)  # get first person in line
            if (curr_time - client.arrival_time) > 15 * 60 and not client.got_service:
                abandoned += 1
                self.n_clients -= 1
                continue
            # if client needs a swap, he will take any elevator down
            if client.need_swap and not elevator.up:
                client.got_service = True
                boarding.append(client)
                client.travelling = True
                client.need_swap = False
                self.n_clients -= 1  # update number of staying in the floor
            elif elevator.up == client.direction and client.desired_floor in elevator.service_floors:
                client.got_service = True
                boarding.append(client)
                client.travelling = True
                self.n_clients -= 1  # update number of staying in the floor
            else:
                staying.append(client)
        if staying:
            for client in staying:
                self.line.append(client)  # push clients back to line
            hpq.heapify(self.line)  # reorder line
        elevator.board_clients(boarding)  # board clients to elevator
        return abandoned

if __name__ == "__main__":
    # test adding and removing from elevator
    pass
