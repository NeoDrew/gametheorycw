import numpy as np

def demand(u_l: float, u_f: float) -> float:
    """Calculate the demand for the leader."""
    return 100 - 5 * u_l + 3 * u_f

def profit(u_l: float, u_f: float) -> float:
    """Calculate the daily profit for the leader."""
    return (u_l - 1.0) * demand(u_l, u_f)

def clip_price(u_l: float, upper_bound: float) -> float:
    """Clip the leader price according to the follower's constraints."""
    lower_bound = 1.0
    return max(lower_bound, min(upper_bound, u_l))
