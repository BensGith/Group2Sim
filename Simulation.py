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

    def get_arrival_rate(self, time_of_day):
        """
        return time between arrivals, depending on the hour
        :param time_of_day:
        :return: time between arrivals
        """
        if 7 <= time_of_day <= 23:
            return np.random.exponential(1)  # 1 min space between arrivals, 60 people an hour
        return np.random.exponential(2)  # 2 min space between arrivals, 30 people an hour

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

    def generate_elevator_arrival_time(self):
        """
        generate a random time for the elevator to arrive
        :return:
        """
        return 1

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
        if not service:
            direction = None
            if client.current_floor > client.desired_floor:
                direction = "down"
            elif client.current_floor < client.desired_floor:
                direction = "up"
            self.order_elevator(current_floor, direction)  # order an elevator to client's floor
        hpq.heappush(self.events, Event(self.curr_time, "arriving"))

    def door_close(self, event):
        travel_time = event.elevator.ride_time()  # pops floor from queue and moves the elevator to next floor
        hpq.heappush(self.events, Event(self.curr_time + travel_time, "door open"))

    def door_open(self, event):
        floor = self.floors[event.floor]
        elevator = self.elevators[event.elevator]
        left_sys = floor.drop_clients(elevator)
        hpq.heappush(self.events, Event(self.curr_time + 5, "door close"))
        floor = event.floor
        elevator = event.elevator

        # floor.drop
        # floor.board
        if elevator.stuck():
            time_to_fix = Elevator.get_fix_time()
            hpq.heappush(self.events, Event(self.curr_time + time_to_fix, "elevator fix"))
            # floor.drop
            pass
        else:
            pass
            # push door open event

    def elevator_fix(self, event):
        hpq.heappush(self.events, Event(self.curr_time, "door open"))

    # def leaving(self, client, elevator):
    #     self.total_clients -= 1
    #
    #     if elevator.stuck():
    #         time_to_fix = Elevator.get_fix_time()
    #         # push control event to heap
    #     # create control, is stuck=true, floor=desired_floor
    #     # else:
    #     # capacity-=1
    #     ride_time = Elevator.ride_time(client.current_floor, client.desired_floor)
    #     # Elevator.floor=client.desired_floor
    #     # go to desired_floor heap remove all until capcaity full and create leaving

    def control(self, elevator):
        elevator.fix_elevator()
        # push leaving

    # stuck=false
    # add time to fix etc self.time = ending fixing time uniform(5,15) min
    # fo to floor's and heap remove all until capcaity full and create leaving

    def order_elevator(self, floor, direction):
        """
        find closest elevator and add the floor desired to its queue
        :param floor: floor the client wants to go from
        :param direction: "up" or "down"
        :return: None
        """
        # score elevators according to their distance from floor given
        # if elevator is going the opposite direction,
        # just add the number of floors it has left to 25 and add 25- desired
        # avoid ordering if elevator present in floor
        closest = 999
        candidate_elevator = None
        for elevator in self.elevators:
            score = 999
            if elevator.up:  # elevator moving up
                if elevator.floor < floor:  # client is above elevator
                    score = floor - elevator.floor
                elif elevator.floor > floor:  # elevator passed the floor
                    score = (25-elevator.floor) + (25-floor)  # first is distance to top, second is from top to request
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
            self.elevators[candidate_elevator].add_to_queue(floor*(-1), direction)
        else:
            self.elevators[candidate_elevator].add_to_queue(floor,
                                                            direction)  # add floor to chosen elevators queue
        # add to next floors set?

    def run(self):
        for i in range(100):
            while self.curr_time < self.simulation_time:
                event = hpq.heappop(self.events)
                if event.event_type == "arriving":
                    self.arriving(event)
                elif event.event_type == "door open":
                    self.door_open(event)
                elif event.event_type == "elevator fix":
                    self.elevator_fix(event)
                elif event.event_type == "door close":
                    self.door_close(event)
