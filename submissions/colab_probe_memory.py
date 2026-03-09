class ProbeLeader(Leader):
    """
    A Memory Probe Leader designed to test if the followers have temporal memory
    (Do they punish us for days? Do they look at averages of our past actions?)
    """
    def __init__(self, name, engine):
        super().__init__(name, engine)
        
        # Test Schedule: 
        # 1. 5 days of £1.00 to establish a flat baseline.
        # 2. A MASSIVE 1-day spike to £100.
        # 3. An immediate return to £1.00 for the next 10 days.
        self.test_prices = (
            [1.0] * 5 +       # Days 101-105: Baseline
            [100.0] +         # Day 106: The shock
            [1.0] * 10        # Days 107-116: The recovery
        )

    def start_simulation(self):
        pass

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def new_price(self, date: int) -> float:
        index = date - 101
        
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev:
                print(f"Day {date-1}: I played £{prev[0]}, Follower reacted with £{prev[1]}")
                
        if index < len(self.test_prices):
            return self.test_prices[index]
            
        return 1.0
        
    def end_simulation(self):
        pass
