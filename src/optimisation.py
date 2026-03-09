import numpy as np
from src.utils import clip_price

def rls_optimal_price(a: float, b: float, upper_bound: float) -> float:
    """
    Calculate the optimal leader price given a linear reaction function: u_F = a + b * u_L
    Profit = (u_L - 1)(100 - 5*u_L + 3*(a + b*u_L))
    
    Returns the valid, clipped optimal price.
    """
    A = 100 + 3 * a
    B = 3 * b - 5
    
    if B >= 0:
        # B == 0: no reaction, profit has no finite max → safe lower bound
        # B >  0: profit is convex (no maximum) → pricing low is safest
        return clip_price(1.0, upper_bound)
        
    u_l_star = (B - A) / (2 * B)
    return clip_price(u_l_star, upper_bound)
