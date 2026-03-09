"""
MONOLITHIC RLS LEADER SCRIPT FOR COLAB
--------------------------------------
This file contains the completely standalone RLS Leader algorithm.
It requires NO local directories to function.

Instructions:
1. Copy everything in this file.
2. Paste it into a new code block in your COMP34612 Google Colab notebook.
3. Run the block.
4. Select "RLSLeaderUnbound" for Mk1/Mk2 opponents, or "RLSLeaderBound" for Mk3.

Why two classes?
  - RLSLeaderUnbound: no price ceiling. Used for Mk1, Mk2 (and likely Mk4/Mk5).
  - RLSLeaderBound:   hard cap at £15. Used for Mk3 (and likely Mk6).
"""

import numpy as np
import pandas as pd
from pathlib import Path


# --- UTILS & OPTIMISATION ---

def clip_price(u_l: float, upper_bound: float) -> float:
    return max(1.0, min(upper_bound, u_l))

def rls_optimal_price(a: float, b: float, upper_bound: float) -> float:
    """
    Closed-form optimal leader price for:
        Profit = (u_L - 1)(100 - 5*u_L + 3*(a + b*u_L))
    Maximised when B < 0 (profit parabola opens downward).
    If B >= 0, the parabola opens up so there is no finite maximum — return lower bound.
    """
    A = 100 + 3 * a
    B = 3 * b - 5
    if B >= 0:
        return clip_price(1.0, upper_bound)
    return clip_price((B - A) / (2 * B), upper_bound)

def load_historical_data(follower_name: str) -> pd.DataFrame:
    """Load historical 100-day data for a given follower from data.xlsx."""
    for path in [Path("data.xlsx"), Path("COMP34612_Student/data.xlsx")]:
        if path.exists():
            try:
                return pd.read_excel(path, sheet_name=f"Follower_{follower_name}")
            except Exception:
                pass
    return pd.DataFrame()

def _init_prior_from_history(follower_name: str):
    """
    Build a safe starting prior from historical data.

    The historical leader NEVER explored beyond ~£1.79, so the linear slope
    (b) CANNOT be estimated reliably from history — the near-zero variance in
    u_L makes OLS estimates of b completely unstable.

    Strategy:
      - a  = mean(historical follower price)   <- reliable
      - b  = 0                                 <- unknown; will be revealed by exploration
      - sigma = std(historical follower price) <- reliable noise estimate

    This places the initial optimal around £11-12, and exploration days 101-105
    (spanning ~£9-18) provide enough u_L variance for RLS to fit the true b.
    """
    df = load_historical_data(follower_name)
    if len(df) > 0:
        y = df["Follower's Price"].values
        # Median-filter to exclude known outliers (e.g., Mk2's £51 spike)
        median_y = np.median(y)
        mad = np.median(np.abs(y - median_y))
        y_clean = y[np.abs(y - median_y) < (5 * mad + 1e-6)]
        a_init = np.mean(y_clean)
        sigma_init = max(np.std(y_clean), 0.05)
    else:
        a_init = 2.0
        sigma_init = 1.0

    theta = np.array([[a_init], [0.0]])   # [a, b=0]
    P = np.eye(2) * 10.0                   # high uncertainty
    return theta, P, sigma_init


# --- LEADER CLASSES ---

class RLSLeaderUnbound(Leader):
    """
    RLS Leader for unbounded followers (Mk1, Mk2, Mk4, Mk5).
    Price is uncapped.
    """
    def __init__(self, name: str, engine):
        super().__init__(name, engine)
        self.lam = 0.90
        self.theta = np.zeros((2, 1))
        self.P = np.eye(2) * 10.0
        self.sigma = 1.0

    def start_simulation(self):
        self.theta, self.P, self.sigma = _init_prior_from_history("Mk1")

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def new_price(self, date: int) -> float:
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev is not None:
                u_L_prev, u_F_prev = prev
                x = np.array([[1.0], [u_L_prev]])
                error = u_F_prev - (self.theta.T @ x)[0, 0]
                # During exploration (days 102-105), ALWAYS update — large errors
                # are the signal we need to learn b, not outliers to reject.
                # After day 105, apply the normal 3-sigma outlier gate.
                in_exploration = (date <= 105)
                if in_exploration or abs(error) < max(3.0 * self.sigma, 1.0):
                    num = self.P @ x @ x.T @ self.P
                    den = self.lam + (x.T @ self.P @ x)[0, 0]
                    self.P = (1.0 / self.lam) * (self.P - num / den)
                    self.theta = self.theta + self.P @ x * error
                    self.sigma = 0.95 * self.sigma + 0.05 * abs(error)

        a, b = self.theta[0, 0], self.theta[1, 0]
        opt = rls_optimal_price(a, b, float('inf'))

        if 101 <= date <= 105:
            schedule = {101: opt, 102: opt + 3.0, 103: opt - 2.0, 104: opt + 6.0, 105: opt - 1.0}
            return clip_price(schedule[date], float('inf'))

        return opt

    def end_simulation(self):
        pass


class RLSLeaderBound(Leader):
    """
    RLS Leader for bounded followers (Mk3, Mk6).
    Price is capped at £15.
    """
    def __init__(self, name: str, engine):
        super().__init__(name, engine)
        self.lam = 0.90
        self.theta = np.zeros((2, 1))
        self.P = np.eye(2) * 10.0
        self.sigma = 1.0

    def start_simulation(self):
        self.theta, self.P, self.sigma = _init_prior_from_history("Mk3")

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def new_price(self, date: int) -> float:
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev is not None:
                u_L_prev, u_F_prev = prev
                x = np.array([[1.0], [u_L_prev]])
                error = u_F_prev - (self.theta.T @ x)[0, 0]
                in_exploration = (date <= 105)
                if in_exploration or abs(error) < max(3.0 * self.sigma, 1.0):
                    num = self.P @ x @ x.T @ self.P
                    den = self.lam + (x.T @ self.P @ x)[0, 0]
                    self.P = (1.0 / self.lam) * (self.P - num / den)
                    self.theta = self.theta + self.P @ x * error
                    self.sigma = 0.95 * self.sigma + 0.05 * abs(error)

        a, b = self.theta[0, 0], self.theta[1, 0]
        opt = rls_optimal_price(a, b, 15.0)

        if 101 <= date <= 105:
            schedule = {101: opt, 102: opt + 3.0, 103: opt - 2.0, 104: opt + 6.0, 105: opt - 1.0}
            return clip_price(schedule[date], 15.0)

        return opt

    def end_simulation(self):
        pass
