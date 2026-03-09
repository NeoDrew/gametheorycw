# COMP34612 — Stackelberg Pricing Game

A repeated 2-person Stackelberg pricing game where we play as the **leader** (price-setter) against various **followers** (competitors). The goal is to maximise accumulated profit over 30 days.

---

## The Game in a Nutshell

```
You (Leader)                          Follower (MK1/MK2/MK3)
     │                                        │
     │── announce price u_L ──────────────────>│
     │                                        │── observes u_L
     │                                        │── picks price u_F
     │<───────────── responds with u_F ───────│
     │                                        │
     │  Your profit = (u_L - 1) × (100 - 5·u_L + 3·u_F)
     │
     └── repeat for 30 days (days 101-130)
```

- **Days 1–100**: Historical data (provided in `data.xlsx`)
- **Days 101–130**: Live game — your code sets prices and receives follower responses

---

## Key Formulas

| Symbol | Meaning | Formula |
|--------|---------|---------|
| `u_L` | Leader's price | Your choice |
| `u_F` | Follower's price | Their response to `u_L` |
| `c_L` | Unit cost | £1.00 (fixed) |
| `S_L` | Sales (demand) | `100 - 5·u_L + 3·u_F` |
| Profit | Daily profit | `(u_L - 1) × S_L` |

**Strategy space bounds**:
- MK1, MK2, MK4, MK5: `u_L ∈ [1.00, +∞)`
- MK3, MK6: `u_L ∈ [1.00, 15.00]`

---

## Project Files

### Platform (provided, do not modify)

```
COMP34612_Student/
├── comp34612.zip          # Upload this to Colab (don't unzip manually)
├── comp34612/             # Unzipped platform (auto-extracted by notebook)
├── data.xlsx              # Historical data: 100 days × 3 followers
├── engine.py              # Game engine (obfuscated)
├── followers.py           # Follower logic (obfuscated)
├── gui.py                 # Simulation GUI (obfuscated)
├── base_follower.py       # Base follower class (obfuscated)
├── constants.py           # Game constants (obfuscated)
├── excel.py               # Data export (obfuscated)
└── comp34612_project.ipynb  # ⭐ THE SUBMISSION NOTEBOOK
```

### Our Code

```
src/                       # Our core engine logic (developed locally)
├── leaders/               # Leader strategy implementations (e.g., rls.py)
├── followers/             # Mock followers for local testing (Mk4/5/6 simulations)
├── utils.py               # Shared helpers (demand, profit, clipping)
├── data_loader.py         # Load historical data
└── optimisation.py        # Price optimisation routines
notebooks/                 # Local dev notebooks (EDA, experiments)
tests/                     # Local simulation tests (e.g., evaluate_rls.py, test_lambda.py)
submissions/               # Final, monolithic Python files ready to be pasted into Google Colab
data/                      # Historical and Colab-generated data (.xlsx)
```

---

## How the Platform API Works

### 1. The Leader Base Class

Every leader must subclass `Leader` (defined in the notebook):

```python
class Leader:
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine

    def new_price(self, date: int) -> float:
        """Called each day (101-130). Return your price for today."""
        pass

    def get_price_from_date(self, date: int) -> tuple:
        """Get (leader_price, follower_price) for any past day (1-130).
        Use this to access historical data or yesterday's result."""
        return self.engine.exposed_get_price(date)

    def start_simulation(self):
        """Called once at the beginning of the 30-day game."""
        pass

    def end_simulation(self):
        """Called once at the end of the 30-day game."""
        pass
```

### 2. Game Flow (what happens when you click "Start Simulation")

```
start_simulation() is called
│
├── Day 101: new_price(101) → you return u_L
│             engine runs follower → u_F is recorded
│             (you can now call get_price_from_date(101) to see u_F)
│
├── Day 102: new_price(102) → you return u_L
│             ...
│
└── Day 130: new_price(130) → you return u_L
              engine runs follower → u_F is recorded
              end_simulation() is called
              total profit is calculated
```

### 3. Accessing Historical Data

There are **two ways** to get past data:

**Option A — Via the engine API (during simulation):**
```python
def new_price(self, date):
    # Get yesterday's prices
    leader_price, follower_price = self.get_price_from_date(date - 1)

    # Get any historical day (1-100)
    l_price, f_price = self.get_price_from_date(42)
```

**Option B — From `data.xlsx` (for pre-training):**
```python
import pandas as pd
df = pd.read_excel("data.xlsx", sheet_name=None)  # dict of DataFrames
# Sheets: 'MK1', 'MK2', 'MK3'
# Columns: 'Day', 'Leader Price', 'Follower Price'
```

### 4. Example: A Simple Leader

```python
class SimpleLeader(Leader):
    def __init__(self, name, engine):
        super().__init__(name, engine)

    def new_price(self, date: int):
        return 1.5 + random.random() * 0.1  # random price ~£1.50
```

### 5. Registering Your Leader

After defining your class, the notebook calls:
```python
engine = Engine()
app = GUI(engine, Leader, group_num)
```
The GUI auto-discovers all `Leader` subclasses and shows them in a dropdown.

---

## How to Run

### On Google Colab (required for submission)

1. Open `comp34612_project.ipynb` on [Google Colab](https://colab.research.google.com)
2. Upload `comp34612.zip` (do **not** unzip)
3. Run the "Install and Import" cells
4. Open the `submissions/` folder in our repository.
5. Copy the entire contents of `colab_rls_leader.py` (or your chosen leader) and paste it into a new cell in Colab.
6. Run the cell, then run the GUI cell. Select your leader and start the simulation!

### Locally (for development)

```bash
# Set up Python environment
uv sync

# Run mathematical evaluations and simulations
uv run python tests/evaluate_rls.py
uv run python tests/test_lambda.py

# Work in notebooks
uv run jupyter lab
```

> ⚠️ The simulation engine **cannot run locally** (PyArmor-obfuscated + Colab-specific).
> Develop and test your learning/optimisation logic locally, then paste into the Colab notebook.

---

## Followers

| Name | Strategy Space | Hidden Variant | Notes |
|------|---------------|----------------|-------|
| MK1 | `[1, +∞)` | MK4 (similar) | Unknown reaction function |
| MK2 | `[1, +∞)` | MK5 (similar) | Unknown reaction function |
| MK3 | `[1, 15]` | MK6 (similar) | Bounded price range |

- MK4/5/6 are **hidden** — tested during marking only
- They have "slightly changed parameters" from MK1/2/3
- Your code must **generalise** (no hardcoding specific to MK1–3)

---

## Assessment

| Component | Weight |
|-----------|--------|
| Presentation (Week 11) | 40% of project |
| Written materials | 10% of project |
| **Code performance** (accumulated profit) | **50% of project** |

Performance is averaged across (MK1+MK4), (MK2+MK5), (MK3+MK6), compared to the best possible profit.

**Constraints**: 10-minute execution time limit, free Google Colab, no exotic dependencies.

---

## Project Status

✅ **Approach 1 Completed: Recursive Least Squares (RLS) Leader**
* Discovered via Colab probes that Mk1, Mk2, and Mk3 have hidden linear reaction functions (historically masked by poor exploration).
* Devised a monolithic `RLSLeader` that deliberately explores for 5 days, mathematically locks onto the hidden function using a heavily defensive `lambda = 0.90` short-term memory, and exploits the followers perfectly using Stackelberg calculus.
* **Profit Achieved:** ~£75,870 across Mk1, Mk2, and Mk3 in under 0.05 seconds of execution time.

🚀 **Next Steps:**
* Finding and designing **Approach 2**, comparing it against RLSLeader.
