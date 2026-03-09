"""
Script to evaluate the RLSLeader using a clean, mocked simulation loop, 
since the raw obfuscated PyArmor Engine cannot be easily imported locally on all environments.
"""

import sys
from pathlib import Path
import numpy as np

# Add the root directory to PYTHONPATH so we can import src 
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.leaders.rls import RLSLeaderUnbound, RLSLeaderBound
from src.data_loader import load_historical_data
from src.utils import profit

class MockEngine:
    def __init__(self, follower_name):
        self.follower_name = follower_name
        self.history = {} # day: (u_L, u_F)
        
        # Load historical data to act as the true "environment" generator
        self.historical_data = load_historical_data(follower_name)
        if len(self.historical_data) > 0:
            self.mean_f = self.historical_data["Follower's Price"].mean()
            self.std_f = self.historical_data["Follower's Price"].std()
        else:
            self.mean_f = 2.0
            self.std_f = 0.5
            
    def exposed_get_price(self, date):
        return self.history.get(date, None)
        
    def simulate_follower_reaction(self, u_L, date):
        """Simulate how the follower reacts to our price."""
        # For Mk1/2/3, we know they basically just pull from a distribution
        # Let's just return a random draw from their historical distribution
        # For Mk2, let's inject a sudden spike on day 115 just to test robust rejection!
        
        if self.follower_name == "Mk2" and date == 115:
            return 50.0 # OUTLIER ATTACK!
            
        # Normal noise
        u_F = max(1.0, np.random.normal(self.mean_f, self.std_f))
        return u_F

def run_evaluation(follower_name):
    print(f"\n{'='*60}")
    print(f"Evaluating RLSLeader against mocked {follower_name}")
    print(f"{'='*60}")
    
    leader_name = f"RLS_{follower_name}"
    engine = MockEngine(follower_name)
    
    leader_class_map = {
        "Mk1": RLSLeaderUnbound,
        "Mk2": RLSLeaderUnbound,
        "Mk3": RLSLeaderBound
    }
    leader = leader_class_map[follower_name](leader_name, engine)
    
    # Init
    leader.start_simulation()
    
    print(f"Initial Model (from 100 days data):")
    print(f"  a = {leader.theta[0,0]:.4f}, b = {leader.theta[1,0]:.4f}")
    print(f"  sigma (noise) = {leader.sigma:.4f}")
    print(f"  Expected Optimal = 10.5 + 0.3*{engine.mean_f:.2f} = {10.5 + 0.3*engine.mean_f:.2f}")
    
    total_profit = 0
    profits = []
    
    print("\nSimulation Log (Days 101-130):")
    for date in range(101, 131):
        # 1. We provide our price
        u_l = leader.new_price(date)
        
        # 2. Follower reacts
        u_f = engine.simulate_follower_reaction(u_l, date)
        
        # 3. Engine records it
        engine.history[date] = (u_l, u_f)
        
        # Calculate profit manually just to track it cleanly
        daily_profit = profit(u_l, u_f)
        total_profit += daily_profit
        profits.append(daily_profit)
        
        if date <= 105 or date == 115 or date == 130 or date % 5 == 0:
            phase = "EXPLORE" if date <= 105 else "EXPLOIT"
            if date == 115 and follower_name == "Mk2":
                phase = "SPIKE!"
            print(f"Day {date} [{phase:7s}]: u_L = £{u_l:5.2f} | u_F = £{u_f:5.2f} | Profit: £{daily_profit:6.2f} | Model: (a={leader.theta[0,0]:5.2f}, b={leader.theta[1,0]:5.2f})")
    
    leader.end_simulation()
    
    print(f"\nFinal Results:")
    print(f"  Total 30-Day Profit: £{total_profit:.2f}")
    print(f"  Average Daily: £{np.mean(profits):.2f}")
    
    return total_profit

if __name__ == "__main__":
    mk1_profit = run_evaluation("Mk1")
    mk2_profit = run_evaluation("Mk2")
    mk3_profit = run_evaluation("Mk3")
    
    print(f"\n{'*'*60}")
    print(f"GRAND TOTAL PROFIT (Mk1+Mk2+Mk3): £{mk1_profit + mk2_profit + mk3_profit:.2f}")
    print(f"{'*'*60}")
