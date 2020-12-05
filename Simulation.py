import numpy as np
import heapq as hpq
from Event import Event
from Floor import Floor
from Elevator import Elevator
from Client import Client
import matplotlib.pyplot as plt

# Assumption - the line in the floor is determined by time spent in floor
# Assumption - if client boarded and elevator got stuck, clients are pushed to the back of the line
# Assumption - if client ordered an elevator and it's full it WILL STOP in that floor like a real elevator
# Assumption - lines are sorted by arrival time


# noinspection DuplicatedCode
class Simulation:
    def __init__(self, saturday=True):

        self.simulation_time = 60 * 60 * 20
        self.curr_time = 21600  # simulation clock starts at 6
        self.floors = [Floor(i) for i in range(26)]
        self.events = []
        self.abandoned = 0
        self.saturday = saturday  # working as a Saturday elevator
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        # metrics to display

        self.service_dist = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}
        self.service_times = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}
        self.capacity_dist = {i: 0 for i in range(16)}  # time distribution of number of passengers in the elevators
        self.elevator_mat = np.zeros((100, 4))  # 100 days per elevator
        self.elevators_avg_cap = [0, 0, 0, 0]
        self.abandoned_lst = []

    def reset_simulation(self, saturday):
        self.curr_time = 21600  # simulation clock starts at 6
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        self.events = []
        self.abandoned = 0
        self.elevators_avg_cap = [0, 0, 0, 0]
        self.saturday = saturday  # working as a Saturday elevator
        self.service_dist = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, 1000: 0}

    def gen_client(self):
        morning = [150, 400, 90, 84, 60, 120, 60, 36]
        afternoon = [90, 120, 150, 84, 60, 400, 60, 36]
        other = [60, 70, 60, 84, 60, 70, 60, 36]
        m_prob = [morning[i] / 1000 for i in range(len(morning))]
        a_prob = [afternoon[i] / 1000 for i in range(len(afternoon))]
        o_prob = [other[i] / 500 for i in range(len(other))]
        rows_in_table = [i for i in range(8)]
        arrivals = [(0, 1), (0, 1), (1, 16), (1, 16), (1, 16), (16, 26), (16, 26), (16, 26)]
        destinations = [(1, 16), (16, 26), (0, 1), (1, 16), (16, 26), (0, 1), (1, 16), (16, 26)]
        if self.curr_time >= 25200 and self.curr_time <= 36000:
            probs = m_prob
            time = 'morning'
        elif self.curr_time >= 54000 and self.curr_time <= 64800:
            probs = a_prob
            time = 'afternoon'
        else:
            probs = o_prob
            time = 'other'

        row = int(np.random.choice(rows_in_table, p=probs, size=1))
        curr_floor = arrivals[row]
        curr_floor = np.random.randint(curr_floor[0], curr_floor[1])
        desired_floor = destinations[row]
        desired_floor_tmp = np.random.randint(desired_floor[0], desired_floor[1])
        while curr_floor == desired_floor_tmp:
            desired_floor_tmp = np.random.randint(desired_floor[0], desired_floor[1])
        desired_floor = desired_floor_tmp
        if time == 'morning':
            y = np.random.exponential(1 / (1000 / 3600))
        elif time == 'afternoon':
            y = np.random.exponential(1 / (1000 / 3600))
        else:
            y = np.random.exponential(1 / (500 / 3600))

        return Client(curr_floor, desired_floor, y + self.curr_time)

    def arriving(self, event):
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
        # don't do anything if it's saturday, elevators

        client = self.gen_client()
        hpq.heappush(self.events, Event(client.arrival_time, "arriving", None, None, client))

    def door_close(self, event):
        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator - 1]
        elevator.doors_open = False
        print("Elevator {} closing at floor {} ob {} dir {}".format(elevator.number, elevator.floor,
                                                                    len(elevator.clients),
                                                                    elevator.up))
        abandoned = floor.board_clients(elevator, self.curr_time)  # add clients that arrived before door closing
        self.abandoned += abandoned
        travel_time = elevator.travel()  # pops floor from queue and moves the elevator to next floor
        print("Elevator {} arrived at floor {} ob {}".format(elevator.number, elevator.floor, len(elevator.clients),
                                                             ))
        # elevator.floor is the new floor the elevator reached
        hpq.heappush(self.events, Event(self.curr_time + travel_time, "door open", elevator.floor, elevator.number))

    def door_open(self, event):

        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator - 1]
        self.update_elevator_capacity(elevator, event.time)  # add number of people to metrics
        elevator.doors_open = True
        service_times = floor.drop_clients(elevator, self.curr_time)  # update Simulation metrics?
        if floor.number == 0 and not self.saturday:
            for client in floor.line:
                if client.got_service and not client.reorder:  # client swapping have to reorder
                    self.order_elevator(0, "up", client.desired_floor)
                    client.reorder = True
        print("Elevator {} open at floor {} ob {} eos {}".format(elevator.number, floor.number, len(elevator.clients),
                                                                 len(service_times)))
        self.update_service_dist(service_times)

        if elevator.stuck():
            time_to_fix = Elevator.get_fix_time()
            hpq.heappush(self.events, Event(self.curr_time + time_to_fix, "elevator fix",
                                            floor.number,
                                            elevator.number))
        else:
            hpq.heappush(self.events, Event(self.curr_time + 5, "door close", elevator.floor, elevator.number))

    def elevator_fix(self, event):
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
            map(lambda x: x[1] / 100, sorted([[key, value] for key, value in sat_sim.service_times.items()],
                                             key=lambda x: x[0])))
        x = ["T<1", "1<T<2", "2<T<3", "3<T<4", "4<T<5", "T>5"]
        plt.bar(x, y, align='center')
        plt.xticks(x)
        plt.xlabel('Service Time [min]')
        plt.ylabel('Number of Clients')
        plt.title('Service Time Distribution')
        plt.show()

    def plot_capcity_dist(self):
        """
        plot service times
        :param matrix: system history matrix
        :return: None
        """
        y = list(
        map(lambda x: x[1] /(4 *60 * 60 * 14), sorted([[key, value] for key, value in sat_sim.capacity_dist.items()],
                                         key=lambda x: x[0])))  # didn't divide to maintain percentage
        x = [i for i in range(16)]
        plt.bar(x, y, align='center')
        plt.xticks(x)
        plt.xlabel('Number of Clients')
        plt.ylabel('Percentage of Time [%]')
        plt.title('Elevator Capacity Distribution')
        plt.show()

    def run(self):

        for i in range(100):
            np.random.seed(i+1)
            self.reset_simulation(self.saturday)
            client = self.gen_client()
            hpq.heappush(self.events, Event(client.arrival_time, "arriving", None, None, client))
            if self.saturday:
                for elevator in self.elevators:
                    hpq.heappush(self.events, Event(self.curr_time, "door open", elevator.floor, elevator.number))
            while self.curr_time < self.simulation_time:
                event = hpq.heappop(self.events)
                self.curr_time = event.time
                if event.event_type == "arriving":
                    self.arriving(event)
                elif event.event_type == "door open":
                    self.door_open(event)
                elif event.event_type == "elevator fix":
                    self.elevator_fix(event)
                elif event.event_type == "door close":
                    self.door_close(event)
            for floor in self.floors:
                for client in floor.line:
                    if (self.curr_time - client.arrival_time) > 15 * 60 and not client.got_service:
                        self.abandoned += 1
            avg_cap = list(map(lambda x: x / (self.curr_time - 21600), self.elevators_avg_cap))
            self.abandoned_lst.append(self.abandoned)
            for key, value in self.service_dist.items():
                self.service_times[key] += value
            for j in range(len(avg_cap)):
                self.elevator_mat[i][j] = avg_cap[j]


if __name__ == "__main__":
    sat_sim = Simulation(False)  # saturday
    sat_sim.run()
    print(sat_sim.service_dist)
    print(sum(sat_sim.abandoned_lst)/100)
    print(list(map(lambda x: x/100, sat_sim.elevator_mat.sum(axis=0))))  # avg capacity per elevator
    service_times = list(map(lambda x: x[1]/100, sorted([[key, value] for key, value in sat_sim.service_times.items()],
                                                   key=lambda x: x[0])))
    capacity_dist = list(
        map(lambda x: x[1] /(4 *60 * 60 * 14), sorted([[key, value] for key, value in sat_sim.capacity_dist.items()],
                                         key=lambda x: x[0])))  # didn't divide to maintain percentage
    sat_sim.plot_capcity_dist()
    print(service_times)
    print(capacity_dist)
    print(sum(capacity_dist))
    sat_sim.plot_service_times()