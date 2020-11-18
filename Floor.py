class Floor:
    def __init__(self, number):
        self.clients = []
        self.number = number
        self.line = []
        self.n_clients = 0

    def update_clients(self,minus):
        self.n_clients -=minus


