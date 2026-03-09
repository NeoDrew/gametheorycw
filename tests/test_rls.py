import pytest
import numpy as np
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.leaders.rls import RLSLeaderUnbound

class DummyEngine:
    def exposed_get_price(self, date):
        # mock returning some prices
        return (1.8, 3.5)

def test_rls_leader_init():
    engine = DummyEngine()
    leader = RLSLeaderUnbound("Test_Mk1", engine)
    
    assert leader.lam == 0.90
    assert leader.theta.shape == (2, 1)

def test_rls_leader_start_simulation():
    engine = DummyEngine()
    leader = RLSLeaderUnbound("Test_Mk2", engine)
    
    # Needs to load data.xlsx for Mk2 silently
    leader.start_simulation()
    
    # Check that theta was initialised to something sensible
    assert leader.theta.shape == (2, 1)
    # P should be positive definite matrix (2x2)
    assert leader.P.shape == (2, 2)
    assert np.all(np.linalg.eigvals(leader.P) > 0)
    
    # Outlier standard deviation should be tracked
    assert leader.sigma > 0

def test_rls_leader_new_price():
    engine = DummyEngine()
    leader = RLSLeaderUnbound("Test_Mk1", engine)
    leader.start_simulation()
    
    # Test exploration phase (Mk1 has no upper bound, so +3 won't be clipped)
    price_101 = leader.new_price(101)
    price_102 = leader.new_price(102)
    assert price_101 != price_102 # Should be different due to exploration schedule
    
    # Test exploitation phase
    price_110 = leader.new_price(110)
    assert price_110 >= 1.0 # Bounds check for Mk1
