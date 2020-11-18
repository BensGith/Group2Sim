class Event:
    def __init__(self, time, event_type, client):
        self.time = time
        self.event_type = event_type
        self.client = client

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return "{} : {}".format(self.event_type, self.time)

