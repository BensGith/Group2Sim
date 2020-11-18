import numpy as np


class Simulation:
    def __init__(self):
        self.sim = 0

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

    def find_day(self,time):
        """
        get the day number of simulation
        :param time: curr_time, simulation clock
        :return: day of simulation (0,1..9)
        """
        return int(time // (24 * 60))
