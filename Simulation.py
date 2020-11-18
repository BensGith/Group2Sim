import numpy as np
import heapq as hpq
from Event import Event
from Floor import Floor
from Elevator import Elevator


# Assumption - the line in the floor is determined by time spent in floor
# Assumption - if client boarded and elevator got stuck, clients are pushed to the back of the line


class Simulation:
    def __init__(self):
        self.simulation_time = 60 * 60 * 24
        self.curr_time = 0  # simulation clock
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i) for i in range(1, 5)]
        self.events = []
        self.total_clients = 0
        self.abandoned = 0

    def reset_simulation(self):
        self.simulation_time = 60 * 60 * 24
        self.curr_time = 0  # simulation clock
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i) for i in range(1, 5)]
        self.events = []
        self.total_clients = 0
        self.abandoned = 0

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

    def arriving(self, event):

        self.total_clients += 1
        client = event.client
        current_floor = client.current_floor
        arrival_time = event.time
        desired_floor = client.desired_floor
        if client.abandon():
            self.total_clients -= 1
            self.abandoned += 1
            pass
            # client.leave_system
        if event.client.need_swap:
            pass
        else:
            pass
        # if elevator in current floor:
        hpq.heappush(self.events, Event(self.curr_time, "door open"))

        hpq.heappush(self.events, Event(self.curr_time, "arriving"))
        # if current_floor== elevator.floor:
        # # capacity+=1
        # remove all until capcaity full and create leaving
        # else:
        # push to current_floor_line_heap
        # create arriving

    def door_close(self, event):
        pass

    def door_open(self, event):
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

    def run(self):
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
