import numpy as np
import heapq as hpq
import Event
from Floor import Floor
from Elevator import Elevator

# Assumption - the line in the floor is determined by time spent in floor


class Simulation:
    def __init__(self):
        self.sim = 0
        self.time = 0  # simulation clock
        self.floors = [Floor(i) for i in range(26)]
        self.elevators = [Elevator(i) for i in range(1, 5)]
        self.events = []

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
        client = event.client
        current_floor = client.current_floor
        arrival_time = event.time
        desired_floor = client.desired_floor
        if client.abandon(self.time):
            pass
            # client.leave_system
        if event.client.need_swap:
            pass
        # if current_floor== elevator.floor:
        # capacity+=1
        # self.swap_elevator()
        # if current_floor== elevator.floor:
        # # capacity+=1
        # remove all until capcaity full and create leaving
        # else:
        # push to current_floor_line_heap
        # create arriving

    def swap_elevator(self,client):
        # change client
        pass

    def leaving(self, client):
        pass
        # if elevator stucked (probability)
        # create control, is stuck=true, floor=desired_floor
        # else:
        #capacity-=1
        ride_time = Elevator.ride_time(client.current_floor, client.desired_floor)
        # Elevator.floor=client.desired_floor
        # go to desired_floor heap remove all until capcaity full and create leaving

    def control(self,floor):
        pass
    # stuck=false
    # add time to fix etc self.time = ending fixing time uniform(5,15) min
    # fo to floor's and heap remove all until capcaity full and create leaving




    def run(self):
        event = Event()

