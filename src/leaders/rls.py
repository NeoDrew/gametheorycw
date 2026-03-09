import numpy as np
from src.optimisation import rls_optimal_price
from src.data_loader import load_historical_data


def _fit_rls_from_history(follower_name: str):
    """
    Bootstrap the RLS model using plain OLS on historical data.
    Uses equal weights (no exponential decay) for a reliable initial estimate.
    Returns (theta, P, sigma). Falls back to a blank prior if no data found.
    """
    df = load_historical_data(follower_name)
    if len(df) > 0:
        x = df["Leader's Price"].values
        y = df["Follower's Price"].values
        # Robust outlier filter
        median_y = np.median(y)
        mad = np.median(np.abs(y - median_y))
        mask = np.abs(y - median_y) < (5 * mad + 1e-6)
        x_clean, y_clean = x[mask], y[mask]
        X_mat = np.column_stack([np.ones_like(x_clean), x_clean])
        # Plain OLS — equal weights, stable over all 100 days
        XT_X = X_mat.T @ X_mat
        if np.linalg.cond(XT_X) > 1e10:
            XT_X += np.eye(2) * 1e-6
        theta = np.linalg.inv(XT_X) @ (X_mat.T @ y_clean.reshape(-1, 1))
        P = np.linalg.inv(XT_X)
        sigma = max(np.std(y_clean - (X_mat @ theta).flatten()), 0.05)
        return theta, P, sigma
    # Blank prior fallback
    return np.array([[2.0], [0.0]]), np.eye(2) * 10.0, 1.0


class RLSLeaderUnbound:
    """
    RLS Leader for unbounded followers (Mk1, Mk2, Mk4, Mk5).
    Warm-starts from Mk1 historical data. Price is uncapped.
    """
    def __init__(self, name: str, engine):
        self.name = name
        self.engine = engine
        self.lam = 0.90
        self.theta = np.zeros((2, 1))
        self.P = np.eye(2) * 10.0
        self.sigma = 1.0

    def start_simulation(self):
        self.theta, self.P, self.sigma = _fit_rls_from_history("Mk1")

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
        opt = rls_optimal_price(a, b, float('inf'))

        if 101 <= date <= 105:
            schedule = {101: opt, 102: opt + 3.0, 103: opt - 2.0, 104: opt + 6.0, 105: opt - 1.0}
            from src.utils import clip_price
            return clip_price(schedule[date], float('inf'))

        return opt

    def end_simulation(self):
        pass


class RLSLeaderBound:
    """
    RLS Leader for bounded followers (Mk3, Mk6).
    Warm-starts from Mk3 historical data. Price capped at £15.
    """
    def __init__(self, name: str, engine):
        self.name = name
        self.engine = engine
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
            from src.utils import clip_price
            return clip_price(schedule[date], 15.0)

        return opt

    def end_simulation(self):
        pass
