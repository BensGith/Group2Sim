class Event:
    def __init__(self, time, event_type, floor=None, elevator=None, client=None):
        """
        floor and elevator are INDEXES!! Simulation object uses that index to find the objects
        :param time: system time
        :param event_type: event types
        :param floor: floor index
        :param elevator: elevator index
        """
        self.time = time
        self.event_type = event_type
        self.floor = floor
        self.elevator = elevator
        self.client = client

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return "{} : {}".format(self.event_type, self.time)

