import numpy as np
import heapq as hpq
from Event import Event
from Floor import Floor
from Elevator import Elevator
from Client import Client


# Assumption - the line in the floor is determined by time spent in floor
# Assumption - if client boarded and elevator got stuck, clients are pushed to the back of the line
# Assumption - if client ordered an elevator and it's full it WILL STOP in that floor like a real elevator
# Assumption - lines are sorted by arrival time


# noinspection DuplicatedCode
class Simulation:
    def __init__(self, saturday=True):
        self.simulation_time = 60 * 60 * 24
        self.curr_time = 25200  # simulation clock starts at 7
        self.floors = [Floor(i) for i in range(26)]
        self.events = []
        self.total_clients = 0
        self.abandoned = 0
        self.saturday = saturday  # working as a Saturday elevator
        self.current_event = None
        self.prv_event = None
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        self.service_dist = {60: 0, 120: 0, 180: 0, 240: 0, 300: 0, "other": 0}

    def reset_simulation(self, saturday=True):
        self.simulation_time = 60 * 60 * 24
        self.curr_time = 0  # simulation clock
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        self.events = []
        self.total_clients = 0
        self.abandoned = 0
        self.saturday = saturday  # working as a Saturday elevator

    def find_hour(self, time):
        """
        function returns which hour of the day is it
        :param time: curr_time, simulation clock
        :return: hour of day (0,1,2,3..23)
        """
        # if sim clock is between 0 and 59.9 return 0, between 60 and 119.9 return 1..
        # floor 60 modulo 24 of sim clock is the hour
        # time floor 24*60 is the day number of the simulation
        # will serve as i,j for system_history
        return int((time // 60) % 24)

    def find_day(self, time):
        """
        get the day number of simulation
        :param time: curr_time, simulation clock
        :return: day of simulation (0,1..9)
        """
        return int(time // (24 * 60))

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
        self.total_clients += 1  # add to total count
        current_floor = client.current_floor  # current floor number, use as index to access floor list
        self.floors[current_floor].add_to_line(client)  # add client to floor's line
        # search for elevator in this floor
        service = False
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
                direction = None
                if client.current_floor > client.desired_floor:
                    direction = "down"
                elif client.current_floor < client.desired_floor:
                    direction = "up"
                self.order_elevator(current_floor, direction, client.desired_floor)
        # don't do anything if it's saturday, elevators

        if self.curr_time < self.simulation_time and self.curr_time <= 72000:
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
        self.total_clients -= abandoned
        travel_time = elevator.travel()  # pops floor from queue and moves the elevator to next floor
        print("Elevator {} arrived at floor {} ob {}".format(elevator.number, elevator.floor, len(elevator.clients),
                                                             ))
        # elevator.floor is the new floor the elevator reached
        hpq.heappush(self.events, Event(self.curr_time + travel_time, "door open", elevator.floor, elevator.number))

    def door_open(self, event):

        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator - 1]
        elevator.doors_open = True
        service_times = floor.drop_clients(elevator, self.curr_time)  # update Simulation metrics?
        if floor.number == 0 and not self.saturday:
            for client in floor.line:
                if client.got_service and not client.reorder:  # client swapping have to reorder
                    self.order_elevator(0, "up", client.desired_floor)
                    client.reorder = True
        print("Elevator {} open at floor {} ob {} eos {}".format(elevator.number, floor.number, len(elevator.clients),
                                                                 len(service_times)))
        self.total_clients -= len(service_times)  # remove clients that left from system
        for time in service_times:
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
                self.service_dist["other"] += 1

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

    def run(self):
        client = self.gen_client()
        hpq.heappush(self.events, Event(client.arrival_time, "arriving", None, None, client))
        if self.saturday:
            for elevator in self.elevators:
                hpq.heappush(self.events, Event(self.curr_time, "door open", elevator.floor, elevator.number))
        for i in range(1):
            # reset simulation
            while self.curr_time < self.simulation_time:
                event = hpq.heappop(self.events)
                self.curr_time = event.time
                # self.update_times(event_time, prv_event_time)
                if event.event_type == "arriving":
                    self.arriving(event)
                elif event.event_type == "door open":
                    self.door_open(event)
                elif event.event_type == "elevator fix":
                    self.elevator_fix(event)
                elif event.event_type == "door close":
                    self.door_close(event)
                # update  system time for clients
                # print(len(self.floors[0].line))
            for floor in self.floors:
                for client in floor.line:
                    if (self.curr_time - client.arrival_time) > 15 * 60 and not client.got_service:
                        self.abandoned += 1


if __name__ == "__main__":
    sat_sim = Simulation(False)  # saturday
    sat_sim.run()
    print(sat_sim.service_dist)
    print(sat_sim.abandoned)
