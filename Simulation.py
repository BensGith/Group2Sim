import numpy as np
import heapq as hpq
from Event import Event
from Floor import Floor
from Elevator import Elevator
from Client import Client


# Assumption - the line in the floor is determined by time spent in floor
# Assumption - if client boarded and elevator got stuck, clients are pushed to the back of the line
# Assumption - if client ordered an elevator and it's full it WILL STOP in that floor like a real elevator


class Simulation:
    def __init__(self, saturday=True):
        self.simulation_time = 60 * 60 * 24
        self.curr_time = 0  # simulation clock
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i, saturday) for i in range(1, 5)]
        self.events = []
        self.total_clients = 0
        self.abandoned = 0
        self.saturday = saturday  # working as a Saturday elevator

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

    def generate_client_arrival(self):
        """
        generate a client with a current floor, desired floor and arrival time
        :return: Client object
        """
        return Client(0, 13, 0.01)  # replace with random generated numbers

    def arriving(self):
        client = self.generate_client_arrival()
        self.total_clients += 1  # add to total count
        current_floor = client.current_floor  # current floor number, use as index to access floor list
        self.floors[current_floor].add_to_line(client)  # add client to floor's line
        # search for elevator in this floor
        service = False
        for elevator in self.elevators:
            # there is an Elevator in the desired floor with closed doors, open doors
            if elevator.floor == current_floor and not elevator.doors_open:
                hpq.heappush(self.events, Event(self.curr_time, "door open", current_floor, elevator.number))
                service = True
                break  # open just one Elevator
        # passengers board on door CLOSE event, take whoever wants to board before they close!
        if not service:  # client did not board elevator
            direction = None
            if client.current_floor > client.desired_floor:
                direction = "down"
            elif client.current_floor < client.desired_floor:
                direction = "up"
            if not self.saturday:  # can't order the elevator on Saturday mode
                # order an elevator to client's floor
                self.order_elevator(current_floor, direction, client.desired_floor)
        if self.curr_time < self.simulation_time:
            hpq.heappush(self.events, Event(self.curr_time, "arriving"))

    def door_close(self, event):
        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator]
        floor.board_clients(elevator)  # add clients that arrived before door closing
        travel_time = event.elevator.travel()  # pops floor from queue and moves the elevator to next floor
        # elevator.floor is the new floor the elevator reached
        hpq.heappush(self.events, Event(self.curr_time + travel_time, "door open", elevator.floor, elevator.number))

    def door_open(self, event):
        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator]
        left_sys = floor.drop_clients(elevator)  # update Simulation metrics?
        if elevator.stuck():
            time_to_fix = Elevator.get_fix_time()
            hpq.heappush(self.events, Event(self.curr_time + time_to_fix, "elevator fix",
                                            floor.number,
                                            elevator.number))
        else:
            hpq.heappush(self.events, Event(self.curr_time + 5, "door close", elevator.floor, elevator.number))

    def elevator_fix(self, event):
        elevator = event.elevator
        self.elevators[elevator].fix_elevator()
        hpq.heappush(self.events, Event(self.curr_time, "door open", event.floor, event.elevator))

    def order_elevator(self, floor, direction, desired_floor):
        """
        find closest elevator and add the floor desired to its queue
        :param floor: floor the client wants to go from
        :param desired_floor: floor the client wants to go to
        :param direction: "up" or "down"
        :return: None
        """
        # score elevators according to their distance from floor given
        # if elevator is going the opposite direction,
        # just add the number of floors it has left to 25 and add 25- desired
        # avoid ordering if elevator present in floor
        closest = 999
        if 16 <= floor <= 25:
            candidate_elevator = 2
        else:
            candidate_elevator = 0
        for elevator in self.elevators:
            if elevator.is_stuck or (floor not in elevator.service_floors):  # can't order that elevator
                continue
            score = 999
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
            if score < closest:
                closest = elevator.floor - floor
                candidate_elevator = elevator.number

        if direction == "down":
            # mul floor by -1 chosen elevators queue, because of down queue takes out the min floor, we need the max one
            self.elevators[candidate_elevator].add_to_queue(floor * (-1), direction)
            # add target floor to queue
            self.elevators[candidate_elevator].add_to_queue(desired_floor * (-1), direction)
        else:  # direction is up
            self.elevators[candidate_elevator].add_to_queue(floor,
                                                            direction)  # add floor to chosen elevators queue
            # add target floor to queue
            self.elevators[candidate_elevator].add_to_queue(desired_floor * (-1), direction)

    def update_times(self, event_time, prv_event_time):
        for floor in self.floors:
            abandon = False
            for client in floor.line:
                if not client.travelling:
                    if client.abandon():
                        self.abandoned += 1
                        abandon = True
                        floor.remove_from_line(client)
                    client.add_wait_time(event_time - prv_event_time)
                client.add_system_time(event_time - prv_event_time)
            if abandon:
                floor.order_line()  # reorder floor line if clients left

    def run(self):
        curr_time = self.generate_client_arrival()
        hpq.heappush(self.events, Event(self.curr_time, "arriving"))
        for i in range(100):
            # reset simulation
            while self.events:
                prv_event = None
                prv_minute = None
                current_minute = None
                event_time = 2
                prv_event_time = 1
                event = hpq.heappop(self.events)
                self.update_times(event_time, prv_event_time)
                if event.event_type == "arriving":
                    self.arriving()
                elif event.event_type == "door open":
                    self.door_open(event)
                elif event.event_type == "elevator fix":
                    self.elevator_fix(event)
                elif event.event_type == "door close":
                    self.door_close(event)
                # update  system time for clients


if __name__ == "main":
    sat_sim = Simulation(True)  # saturday
    sat_sim.run()
    reg_sim = Simulation()
    reg_sim.run()
