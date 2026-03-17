"""
BAYESIAN ADAPTIVE LEADER — COLAB SCRIPT
----------------------------------------
Copy everything below into a new code cell in your COMP34612 notebook and run it.

Select "BayesianLeaderUnbound" for Mk1/Mk2 (and likely Mk4/Mk5).
Select "BayesianLeaderBound"   for Mk3 (and likely Mk6).

Improvements over the RLS baseline:
  1. Informed prior on b (0.4 instead of 0.0) — day-1 price is already reasonable
  2. Shorter exploration (3 days vs 5) — 2 extra days of near-optimal pricing
  3. Adaptive forgetting factor (starts 0.97, adjusts based on prediction errors)
  4. Robust outlier rejection via predictive distribution (handles Mk2-style spikes)
"""

import numpy as np
import pandas as pd
from pathlib import Path


# --- UTILS ---

def clip_price(u_l: float, upper_bound: float) -> float:
    return max(1.0, min(upper_bound, u_l))


def optimal_price(a: float, b: float, upper_bound: float) -> float:
    """
    Closed-form Stackelberg optimal leader price.
    Profit = (u_L - 1)(100 - 5*u_L + 3*(a + b*u_L))
    """
    A = 100 + 3 * a
    B = 3 * b - 5
    if B >= 0:
        return clip_price(1.0, upper_bound)
    return clip_price((B - A) / (2 * B), upper_bound)


def load_historical_data(follower_name: str) -> pd.DataFrame:
    for path in [Path("data.xlsx"), Path("COMP34612_Student/data.xlsx")]:
        if path.exists():
            try:
                return pd.read_excel(path, sheet_name=f"Follower_{follower_name}")
            except Exception:
                pass
    return pd.DataFrame()


def _build_prior(follower_name: str):
    """
    Informed Bayesian prior from historical data.

    Historical u_L has near-zero variance, so b cannot be estimated from history.
    We set b = 0.4 (weak positive) based on the knowledge that all known followers
    have positive reaction slopes (b in [0.04, 0.81]).
    """
    df = load_historical_data(follower_name)
    if len(df) > 0:
        y = df["Follower's Price"].values
        median_y = np.median(y)
        mad = np.median(np.abs(y - median_y))
        y_clean = y[np.abs(y - median_y) < (5 * mad + 1e-6)]
        a_init = float(np.mean(y_clean))
        sigma_init = max(float(np.std(y_clean)), 0.05)
    else:
        a_init = 2.0
        sigma_init = 1.0

    theta = np.array([[a_init], [0.4]])
    P = np.array([[1.0, 0.0],
                  [0.0, 2.0]])
    return theta, P, sigma_init


# --- LEADER CLASSES ---

class BayesianLeaderUnbound(Leader):
    """
    Bayesian Adaptive Leader for unbounded followers (Mk1, Mk2, Mk4, Mk5).

    Exploration: days 101-103 (3 days: optimal, high probe, low probe)
    Exploitation: days 104-130 (27 days of near-optimal pricing)
    Adaptive lambda: 0.97 base, adjusts 0.88-0.99 based on error trends
    """
    def __init__(self, name: str, engine):
        super().__init__(name, engine)
        self.theta = np.zeros((2, 1))
        self.P = np.eye(2) * 10.0
        self.sigma = 1.0
        self.n_obs = 0
        self.lam = 0.97
        self.recent_errors = []

    def start_simulation(self):
        self.theta, self.P, self.sigma = _build_prior("Mk1")

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def _update(self, u_L, u_F):
        x = np.array([[1.0], [u_L]])
        pred = (self.theta.T @ x)[0, 0]
        error = u_F - pred

        # Predictive std for outlier gating
        pred_var = self.sigma**2 * (1.0 + (x.T @ self.P @ x)[0, 0])
        pred_std = max(np.sqrt(pred_var), 0.1)

        # Always accept during exploration; gate after with 4-sigma threshold
        if self.n_obs > 3 and abs(error) > 4.0 * pred_std:
            return

        # Kalman/RLS update with forgetting
        num = self.P @ x @ x.T @ self.P
        den = self.lam + (x.T @ self.P @ x)[0, 0]
        self.P = (1.0 / self.lam) * (self.P - num / den)
        self.theta = self.theta + self.P @ x * error

        # Noise tracking
        self.sigma = 0.9 * self.sigma + 0.1 * abs(error)
        self.sigma = max(self.sigma, 0.05)

        # Adaptive lambda
        self.recent_errors.append(abs(error))
        if len(self.recent_errors) > 10:
            self.recent_errors.pop(0)
        self.n_obs += 1

        if len(self.recent_errors) >= 3:
            recent_mean = np.mean(self.recent_errors[-5:])
            if recent_mean > 2.0 * self.sigma:
                self.lam = max(self.lam - 0.02, 0.88)
            elif recent_mean < 0.5 * self.sigma:
                self.lam = min(self.lam + 0.01, 0.99)

    def new_price(self, date: int) -> float:
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev is not None:
                self._update(prev[0], prev[1])

        a, b = self.theta[0, 0], self.theta[1, 0]
        opt = optimal_price(a, b, float('inf'))

        # Short exploration: 3 days instead of 5
        if date == 101:
            return clip_price(opt, float('inf'))
        elif date == 102:
            return clip_price(opt + 4.0, float('inf'))
        elif date == 103:
            return clip_price(opt - 3.0, float('inf'))

        return opt

    def end_simulation(self):
        pass


class BayesianLeaderBound(Leader):
    """
    Bayesian Adaptive Leader for bounded followers (Mk3, Mk6).
    Same algorithm, price capped at £15.
    """
    def __init__(self, name: str, engine):
        super().__init__(name, engine)
        self.theta = np.zeros((2, 1))
        self.P = np.eye(2) * 10.0
        self.sigma = 1.0
        self.n_obs = 0
        self.lam = 0.97
        self.recent_errors = []

    def start_simulation(self):
        self.theta, self.P, self.sigma = _build_prior("Mk3")

    def get_price_from_date(self, date: int):
        if hasattr(self.engine, 'exposed_get_price'):
            return self.engine.exposed_get_price(date)
        return None

    def _update(self, u_L, u_F):
        x = np.array([[1.0], [u_L]])
        pred = (self.theta.T @ x)[0, 0]
        error = u_F - pred
        pred_var = self.sigma**2 * (1.0 + (x.T @ self.P @ x)[0, 0])
        pred_std = max(np.sqrt(pred_var), 0.1)
        if self.n_obs > 3 and abs(error) > 4.0 * pred_std:
            return
        num = self.P @ x @ x.T @ self.P
        den = self.lam + (x.T @ self.P @ x)[0, 0]
        self.P = (1.0 / self.lam) * (self.P - num / den)
        self.theta = self.theta + self.P @ x * error
        self.sigma = 0.9 * self.sigma + 0.1 * abs(error)
        self.sigma = max(self.sigma, 0.05)
        self.recent_errors.append(abs(error))
        if len(self.recent_errors) > 10:
            self.recent_errors.pop(0)
        self.n_obs += 1
        if len(self.recent_errors) >= 3:
            recent_mean = np.mean(self.recent_errors[-5:])
            if recent_mean > 2.0 * self.sigma:
                self.lam = max(self.lam - 0.02, 0.88)
            elif recent_mean < 0.5 * self.sigma:
                self.lam = min(self.lam + 0.01, 0.99)

    def new_price(self, date: int) -> float:
        if date > 101:
            prev = self.get_price_from_date(date - 1)
            if prev is not None:
                self._update(prev[0], prev[1])

        a, b = self.theta[0, 0], self.theta[1, 0]
        opt = optimal_price(a, b, 15.0)

        if date == 101:
            return clip_price(opt, 15.0)
        elif date == 102:
            return clip_price(opt + 3.0, 15.0)
        elif date == 103:
            return clip_price(opt - 2.0, 15.0)

        return opt

    def end_simulation(self):
        pass
