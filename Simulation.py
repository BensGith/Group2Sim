import numpy as np
import heapq as hpq
from Event import Event
from Floor import Floor
from Elevator import Elevator
from Client import Client
import matplotlib.pyplot as plt


# ##### default mode is set to Saturday #####


# noinspection DuplicatedCode
class Simulation:
    def __init__(self, saturday):

        self.simulation_time = 60 * 60 * 20  # simulation runs until 20:00
        self.curr_time = 21600  # simulation clock starts at 6am
        self.floors = [Floor(i) for i in range(26)]  # creates 25 Floor objects
        self.events = []  # events heap
        self.abandoned = 0  # number of abandoning clients
        self.saturday = saturday  # working as a Saturday/Suggested elevator (True/False)
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]  # create 4 Elevator objects

        # ##### metrics to display #####
        # create service times distribution dictionary
        self.service_dist = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}  # overall
        self.service_times = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}  # temporary
        self.capacity_dist = {i: 0 for i in range(16)}  # time distribution of number of passengers in the elevators
        self.elevator_mat = np.zeros((100, 4))  # 100 days per elevator
        self.elevators_avg_cap = [0, 0, 0, 0] #
        self.abandoned_lst = []

    def reset_simulation(self, saturday):
        """
        method to reset a simulation day  to start the day
        :param saturday: boolean, depending on the Saturday/Suggested mode
        :return: None
        """
        self.curr_time = 21600  # simulation clock starts at 6am
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        self.events = []
        self.abandoned = 0
        self.elevators_avg_cap = [0, 0, 0, 0]
        self.saturday = saturday  # working as a Saturday elevator
        self.service_dist = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}

    def gen_client(self):
        """
        generates Client object with arrival time, desired floor, and current floor

        :return: Client object
        """
        # initializing the arrival rates
        morning = [150, 400, 90, 84, 60, 120, 60, 36]
        afternoon = [90, 120, 150, 84, 60, 400, 60, 36]
        other = [60, 70, 60, 84, 60, 70, 60, 36]
        # creating morning/afternoon/other arrival probabilities
        m_prob = [morning[i] / 1000 for i in range(len(morning))]
        a_prob = [afternoon[i] / 1000 for i in range(len(afternoon))]
        o_prob = [other[i] / 500 for i in range(len(other))]
        rows_in_table = [i for i in range(8)]  # each row represents a row in the given arrival rates table
        # each tuple represents a cell in the given arrival rates table
        arrivals = [(0, 1), (0, 1), (1, 16), (1, 16), (1, 16), (16, 26), (16, 26), (16, 26)]
        # each tuple represents a cell in the given arrival rates table
        destinations = [(1, 16), (16, 26), (0, 1), (1, 16), (16, 26), (0, 1), (1, 16), (16, 26)]
        # matching the probabilities to time of simulation clock
        if self.curr_time >= 25200 and self.curr_time <= 36000:
            probs = m_prob
            time = 'morning'
        elif self.curr_time >= 54000 and self.curr_time <= 64800:
            probs = a_prob
            time = 'afternoon'
        else:
            probs = o_prob
            time = 'other'
        # generating a client curr_floor, desired_floor
        row = int(np.random.choice(rows_in_table, p=probs, size=1))
        curr_floor = arrivals[row]
        curr_floor = np.random.randint(curr_floor[0], curr_floor[1])
        desired_floor = destinations[row]
        desired_floor_tmp = np.random.randint(desired_floor[0], desired_floor[1])
        # if we created the client's desired floor as his arrival floor, choose another floor
        while curr_floor == desired_floor_tmp:
            desired_floor_tmp = np.random.randint(desired_floor[0], desired_floor[1])
        desired_floor = desired_floor_tmp
        # generate arrival time
        if time == 'morning':
            y = np.random.exponential(1 / (1000 / 3600))
        elif time == 'afternoon':
            y = np.random.exponential(1 / (1000 / 3600))
        else:
            y = np.random.exponential(1 / (500 / 3600))

        return Client(curr_floor, desired_floor, y + self.curr_time)

    def arriving(self, event):
        """
        arriving scenario
        :param event: Event object
        :return:
        """
        client = event.client
        current_floor = client.current_floor  # current floor number, use as index to access floor list
        self.floors[current_floor].add_to_line(client)  # add client to floor's line
        # search for elevator in this floor
        if not self.saturday:
            for elevator in self.elevators:
                # there is an Elevator in the desired floor with closed doors, open doors
                if not elevator.start:
                    if elevator.floor == current_floor and not elevator.doors_open and client.desired_floor in elevator.service_floors:
                        elevator.start = True  # elevator won't open while moving
                        hpq.heappush(self.events,
                                     Event(client.arrival_time, "door open", current_floor, elevator.number))
                        break  # open just one Elevator
            if client.need_swap:  # add current and target floors to queue
                self.order_elevator(current_floor, "down", 0)
            else:  # client doesn't need swap
                direction = None  # if client arrived to a floor with an open elevator, do nothing
                if client.current_floor > client.desired_floor:
                    direction = "down"
                elif client.current_floor < client.desired_floor:
                    direction = "up"
                self.order_elevator(current_floor, direction, client.desired_floor)
        # don't do anything if it's Saturday elevators

        client = self.gen_client()
        hpq.heappush(self.events, Event(client.arrival_time, "arriving", None, None, client))

    def door_close(self, event):
        """
        door close scenario
        :param event: Event object
        :return:
        """
        floor = self.floors[event.floor]  # set floor variable to Floor object
        elevator = self.elevators[event.elevator - 1]  # set Elevator variable to Elevator object
        elevator.doors_open = False
        abandoned = floor.board_clients(elevator, self.curr_time)  # add clients that arrived before door closing
        self.abandoned += abandoned  # add abandoning clients to count
        travel_time = elevator.travel()  # pops floor from queue and moves the elevator to next floor
        # elevator.floor is the new floor the elevator reached
        hpq.heappush(self.events, Event(self.curr_time + travel_time, "door open", elevator.floor, elevator.number))

    def door_open(self, event):
        """
        door open scenario
        :param event: Event object
        :return:
        """
        floor = self.floors[event.floor] # set floor variable to Floor object
        elevator = self.elevators[event.elevator - 1] # set Elevator variable to Elevator object
        self.update_elevator_capacity(elevator, event.time)  # add number of people to metrics
        elevator.doors_open = True
        service_times = floor.drop_clients(elevator, self.curr_time)  # update Simulation metrics?
        if floor.number == 0 and not self.saturday:
            for client in floor.line:
                if client.got_service and not client.reorder:  # client swapping have to reorder
                    self.order_elevator(0, "up", client.desired_floor)
                    client.reorder = True
        self.update_service_dist(service_times)
        if elevator.stuck():  # if the elevator got stuck, get a fix time, push elevator fix event to event queue
            time_to_fix = Elevator.get_fix_time()
            hpq.heappush(self.events, Event(self.curr_time + time_to_fix, "elevator fix",
                                            floor.number,
                                            elevator.number))
        else:  # close elevator doors
            hpq.heappush(self.events, Event(self.curr_time + 5, "door close", elevator.floor, elevator.number))

    def elevator_fix(self, event):
        """
        push door open after elevator fix event to events heap
        :param event:
        :return:
        """
        elevator = event.elevator
        self.elevators[elevator - 1].fix_elevator()
        hpq.heappush(self.events, Event(self.curr_time, "door open", event.floor, event.elevator))

    def order_elevator(self, floor, direction, desired_floor):
        """
        find closest elevator and add the floor desired to its queue
        :param floor: floor the client wants to go from
        :param desired_floor: floor the client wants to go to
        :param direction: "up" or "down"
        :return: None
        """
        # if swap is needed, desired floor will be 0
        # score elevators according to their distance from floor given
        # if elevator is going the opposite direction,
        # just add the number of floors it has left to 25 and add 25- desired
        # avoid ordering if elevator present in floor
        closest = 999
        # set default elevator to be ordered
        if 0 <= floor <= 15 and 0 <= desired_floor <= 15:  # lower range
            candidate_elevator = 0
        elif (floor >= 16 or floor == 0) and (desired_floor >= 16 or desired_floor == 0):  # upper range
            candidate_elevator = 2
        else:
            candidate_elevator = 2
            print("Error")
        for elevator in self.elevators:
            # elevator not stuck and must be able to reach from client's floor to desired floor
            # desired floor will be 0 if client wants a swap
            # if one of the conditions is true, don't order that elevator!
            if elevator.is_stuck or (
                    floor not in elevator.service_floors or desired_floor not in elevator.service_floors):  # can't order that elevator
                continue
            score = 999
            if not elevator.up_set or not elevator.down_set:
                candidate_elevator = elevator.number - 1
                break
            if elevator.up:  # elevator moving up
                if elevator.floor < floor:  # client is above elevator
                    score = floor - elevator.floor
                elif elevator.floor > floor:  # elevator passed the floor
                    score = (25 - elevator.floor) + (
                            25 - floor)  # first is distance to top, second is from top to request
            else:  # elevator going down
                if elevator.floor > floor:  # client is below elevator
                    score = elevator.floor - floor
                elif elevator.floor < floor:  # elevator passed the floor
                    score = elevator.floor + floor  # first is distance to bottom, second is from bottom to request
            if score < closest and score != 0:  # don't order an elevator that is in that floor
                closest = score
                candidate_elevator = elevator.number - 1
        elevator = self.elevators[candidate_elevator]
        elevator.add_to_queue([floor, desired_floor], direction)

    def update_service_dist(self, service_lst):
        """
        updating the service times distribution
        :param service_lst: times list
        :return:
        """
        for time in service_lst:
            if time <= 60:
                self.service_dist[60] += 1
            elif time <= 120:
                self.service_dist[120] += 1
            elif time <= 180:
                self.service_dist[180] += 1
            elif time <= 240:
                self.service_dist[240] += 1
            elif time <= 300:
                self.service_dist[300] += 1
            else:
                self.service_dist[1000] += 1

    def update_elevator_capacity(self, elevator, time):
        """
        update the elevator capacity to dictionary to log capacity distribution metric
        :param elevator: Elevator
        :param time:
        :return:
        """
        self.elevators_avg_cap[elevator.number - 1] += len(elevator.clients) * (time - elevator.prv_open_time)
        self.capacity_dist[len(elevator.clients)] += (time - elevator.prv_open_time)
        elevator.prv_open_time = time

    def plot_service_times(self):
        """
        plot service times
        :param matrix: system history matrix
        :return: None
        """
        y = list(
            map(lambda x: x[1] / 100, sorted([[key, value] for key, value in self.service_times.items()],
                                             key=lambda x: x[0])))
        x = ["T<1", "1<T<2", "2<T<3", "3<T<4", "4<T<5", "T>5"]
        plt.bar(x, y, align='center')
        plt.xticks(x)
        plt.xlabel('Service Time [min]')
        plt.ylabel('Number of Clients')
        if self.saturday:
            plt.title('Service Time Distribution - Saturday')
        else:
            plt.title('Service Time Distribution - Suggested')
        plt.show()

    def plot_capcity_dist(self):
        """
        plot service times
        :param matrix: system history matrix
        :return: None
        """
        y = list(
        map(lambda x: x[1] /(4 *60 * 60 * 14), sorted([[key, value] for key, value in self.capacity_dist.items()],
                                         key=lambda x: x[0])))  # didn't divide to maintain percentage
        x = [i for i in range(16)]
        plt.bar(x, y, align='center')
        plt.xticks(x)
        plt.xlabel('Number of Clients')
        plt.ylabel('Percentage of Time [%]')
        if self.saturday:
            plt.title('Elevator Capacity Distribution - Saturday')
        else:
            plt.title('Elevator Capacity Distribution - Suggested')
        plt.show()

    def run(self):
        """
        main method that controls the simulation
        :return: None
        """

        for i in range(100):
            np.random.seed(i+1)  # create different seed for every day
            self.reset_simulation(self.saturday)  # create a new day
            client = self.gen_client()  # generate first client of the day
            # push to event queue first client's arrival
            hpq.heappush(self.events, Event(client.arrival_time, "arriving", None, None, client))
            if self.saturday:  # if saturday mode, push door open event for all elevators
                for elevator in self.elevators:
                    hpq.heappush(self.events, Event(self.curr_time, "door open", elevator.floor, elevator.number))
            while self.curr_time < self.simulation_time:  # while simulation clock is earlier than 20:00
                event = hpq.heappop(self.events)
                self.curr_time = event.time
                # case for dealing with different event types
                if event.event_type == "arriving":
                    self.arriving(event)
                elif event.event_type == "door open":
                    self.door_open(event)
                elif event.event_type == "elevator fix":
                    self.elevator_fix(event)
                elif event.event_type == "door close":
                    self.door_close(event)
            for floor in self.floors:  # update abandoning clients after 20:00 (end of service)
                for client in floor.line:
                    if (self.curr_time - client.arrival_time) > 15 * 60 and not client.got_service:
                        self.abandoned += 1
            # normalize capacity values
            avg_cap = list(map(lambda x: x / (self.curr_time - 21600), self.elevators_avg_cap))
            self.abandoned_lst.append(self.abandoned)
            # update service time distribution dictionary
            for key, value in self.service_dist.items():
                self.service_times[key] += value
            # update capacity matrix
            for j in range(len(avg_cap)):
                self.elevator_mat[i][j] = avg_cap[j]


if __name__ == "__main__":
    # ##### Saturday Mode #####
    print('\n##### Saturday Mode #####')
    print('\nSimulation is running...')
    sat_sim = Simulation(True)  # True if it's Saturday
    sat_sim.run()  # starting the simulation on Saturday mode
    print('Done!')
    print("\nAverage Number of Abandoning Clients: {}".format(sum(sat_sim.abandoned_lst) / 100))
    print("\nAverage Elevators Capacity:\n")
    print(list(map(lambda x: x/100, sat_sim.elevator_mat.sum(axis=0))))  # avg capacity per elevator
    service_times = list(map(lambda x: x[1]/100, sorted([[key, value] for key, value in sat_sim.service_times.items()],
                                                   key=lambda x: x[0])))  # requested service times metric
    capacity_dist = list(
        map(lambda x: x[1] /(4 *60 * 60 * 14), sorted([[key, value] for key, value in sat_sim.capacity_dist.items()],
                                         key=lambda x: x[0])))
    sat_sim.plot_capcity_dist()
    print("\nService Times Distribution Graph Values\n")
    print(service_times)
    print("\nElevator Capacity Distribution Graph Values\n")
    print(capacity_dist)
    sat_sim.plot_service_times()

    # ##### Suggested Mode #####
    print('\n##### Suggested Mode #####')
    print('\nSimulation is running...')
    reg_sim = Simulation(False)  # True if it's Saturday
    reg_sim.run()  # starting the simulation on Saturday mode
    print('Done!')
    print("\nAverage Number of Abandoning Clients: {}".format(sum(reg_sim.abandoned_lst) / 100))
    print("\nAverage Elevators Capacity:\n")
    print(list(map(lambda x: x / 100, reg_sim.elevator_mat.sum(axis=0))))  # avg capacity per elevator
    service_times = list(
        map(lambda x: x[1] / 100, sorted([[key, value] for key, value in reg_sim.service_times.items()],
                                         key=lambda x: x[0])))
    capacity_dist = list(
        map(lambda x: x[1] / (4 * 60 * 60 * 14), sorted([[key, value] for key, value in reg_sim.capacity_dist.items()],
                                                        key=lambda x: x[0])))  # didn't divide to maintain percentage
    reg_sim.plot_capcity_dist()
    print("\nService Times Distribution Graph Values\n")
    print(service_times)
    print("\nElevator Capacity Distribution Graph Values\n")
    print(capacity_dist)
    reg_sim.plot_service_times()

