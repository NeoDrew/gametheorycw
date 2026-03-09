def test_demand():
    from src.utils import demand
    # 100 - 5(2) + 3(3) = 100 - 10 + 9 = 99
    assert demand(2.0, 3.0) == 99.0

def test_profit():
    from src.utils import profit
    # (2 - 1) * 99 = 99
    assert profit(2.0, 3.0) == 99.0

def test_clip():
    from src.utils import clip_price
    assert clip_price(0.5, float('inf')) == 1.0
    assert clip_price(20.0, float('inf')) == 20.0
    
    assert clip_price(0.5, 15.0) == 1.0
    assert clip_price(20.0, 15.0) == 15.0
    
def test_rls_optimal():
    from src.optimisation import rls_optimal_price
    # Assume a = 0, b = 0 (no reaction, just 100 mean demand if u_f=0)
    # A = 100, B = -5
    # u_l* = (-5 - 100) / -10 = 10.5
    assert rls_optimal_price(0.0, 0.0, float('inf')) == 10.5
    
    # Mk3 optimal with large a,b causing it to hit bounds
    # A = 100 + 3(10) = 130
    # B = 3(1) - 5 = -2
    # u_l* = (-2 - 130) / -4 = 33
    # Should clip to 15 for Mk3
    assert rls_optimal_price(10.0, 1.0, 15.0) == 15.0
