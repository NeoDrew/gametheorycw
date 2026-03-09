class ProbeLeader(Leader):
    def __init__(self, name, engine):
        super().__init__(name, engine)
        
        # We will test these specific prices in order on days 101-110
        self.test_prices = [
            1.0,   # Minimum boundary
            5.0,   # Moderate increase
            10.0,  # High
            15.0,  # Mk3/Mk6 Maximum boundary
            25.0,  # Extreme
            50.0,  # Ridiculous
            100.0, # Astronomical
            1.0,   # Back to minimum (Does it have memory?)
            10.0,  # Back to high
            2.0    # Normal
        ]

    def start_simulation(self):
        pass

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def new_price(self, date: int) -> float:
        # For the first 10 days, use our hardcoded test values
        index = date - 101
        
        # Just to print the actual reaction from the previous day directly in the Colab output:
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev:
                print(f"Day {date-1}: I played £{prev[0]}, Follower reacted with £{prev[1]}")
                
        if index < len(self.test_prices):
            return self.test_prices[index]
        
        return 5.0
        
    def end_simulation(self):
        pass
