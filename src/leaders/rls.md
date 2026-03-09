# Approach 1: Recursive Least Squares Leader

## Overview

The `RLSLeader` is a highly robust, adaptive pricing agent built specifically to handle the noise, lack of historical exploration, and sudden outliers present in the Game Theory CW followers. 

It implements **Recursive Least Squares (RLS) with Exponential Forgetting, Outlier Rejection, and Stackelberg Optimal Response**. 

### How It Works (In Simple English)

Imagine you are trying to guess how a competitor will price their product tomorrow based on what you price yours today. 

At first, you only have old data where your company never changed its price (always charging £1.79). Because your price never changed, you have absolutely no idea if the competitor would react if you suddenly doubled your price. 

**Here is what the RLS Leader does to solve this:**
1. **The Shake-Up (Days 1-5)**: Instead of playing it safe, our algorithm deliberately tests the competitor by throwing wildly different prices at them (like £1, £10, £15). This forces the competitor to show their hand and react.
2. **The Fast Learner (Recursive Least Squares)**: Every single day, after we see how the competitor reacted, the algorithm instantly updates its internal guess of how the competitor behaves. It doesn't recalculate everything from scratch; it just nudges its current guess slightly based on the new information ("Recursive"). 
3. **Short-Term Memory (Forgetting Factor)**: It purposefully "forgets" really old data, prioritizing how the competitor is acting *right now*. If the competitor changes their strategy halfway through the month, our algorithm adapts almost immediately.
4. **The BS Detector (Outlier Rejection)**: If the competitor randomly prices at £50 for one day due to a glitch, the algorithm says, "That makes no sense," ignores that day entirely, and protects its internal logic from getting messed up.
5. **The Kill Shot (Exploitation)**: Once the algorithm has figured out exactly how the competitor reacts, it uses high school calculus to find the absolute maximum peak of profit we can mathematically squeeze out of them, and it charges exactly that peak price every single day.

---

### The Problem it Solves
The EDA revealed that the historical leader priced within an extremely narrow band (~£1.79). This lack of exploration meant we could not cleanly observe a linear reaction function (`u_F = a + b * u_L`) for followers Mk1, Mk2, or Mk3. They appeared to just draw from a random distribution. 

If we simply assumed no reaction function exists (and just optimized against their mean price), we would leave massive profit on the table if the hidden followers (Mk4/Mk5/Mk6) *do* possess a reaction function.

### The Hybrid Solution
The `RLSLeader` solves this by gracefully handling both scenarios:
1. If the follower has no reaction function (like Mk1/2/3), the RLS parameter `b` tends heavily towards 0, and the model automatically degrades into simple Mean-Tracking (Distribution Approach).
2. If we discover a reaction function (because we explicitly explore the price space), the model captures `b > 0` and modifies our optimal price to exploit it.

## The Four Core Layers

### Layer 1: The Reaction Function Model
We model the follower's price as:
`follower_price = a + b * leader_price`
Initially, `a` and `b` are estimated using standard Weighted Least Squares on the 100 days of historical data.

### Layer 2: Recursive Least Squares with Forgetting
We track the follower's parameters `[a, b]` as a state vector $\theta$. Every day, after observing the follower's actual price $u_F$, we calculate our prediction error and update our parameters. 
We use a universal **forgetting factor of `lambda = 0.90`**. This intentionally short memory gives the Leader an aggressive shield—prioritizing hyper-fast recovery from massive outliers (like Mk2's historic error) and instant adaptation to hidden tracking mechanics, rather than theoretical stability.

### Layer 3: Robust Outlier Rejection
Mk2's historical data contains a massive anomaly (Spiking to £51 on Day 35). Without protection, a spike like this will immediately drag our RLS estimates into invalid territory.

The `RLSLeader` tracks a rolling estimate of the follower's standard deviation ($\sigma$). If the follower's price prediction error is greater than $3\sigma$, **the observation is rejected as an anomaly**. The RLS model is simply not updated that day. 

*(A mocked simulation verified the leader perfectly ignores a simulated £50 spike on Day 115 without losing profitability!)*

### Layer 4: Stackelberg Optimal Response
With our current estimates of `a` and `b`, our expected daily profit function depends entirely on our own price $u_L$:
Profit = $(u_L - 1)(100 + 3a + (3b - 5)u_L)$

We analytically solve for the vertex of this parabola:
$u_L^* = \frac{3b - 5 - 100 - 3a}{2(3b - 5)}$

We then strictly clip $u_L^*$ to be $\ge 1.0$, and specifically clip Mk3/Mk6 to be $\le 15.0$ to respect the platform's strategy space bounds.

## Active Exploration Phase
Because historical data lacked exploration, we do not have enough variance in $u_L$ to accurately estimate `b`. 
To fix this, the leader plays a hardcoded "Explore" schedule for the first 5 days of the live game (Days 101-105):
- **Day 101:** Optimal calculation
- **Day 102:** Optimal + 3.0
- **Day 103:** Optimal - 2.0
- **Day 104:** Optimal + 6.0
- **Day 105:** Optimal - 1.0

This injects the necessary variance to force the follower to reveal any dormant reaction function. From Day 106 onwards, the leader switches to Pure Exploitation, running precisely $u_L^*$ every single day.

## Performance Evaluation (Live Colab Engine)

After running the RLS Leader against the actual obfuscated PyArmor Engine in Google Colab, the results were extraordinary. 

To evaluate the algorithm's mechanism, we first ran a "Probe Leader" that injected extreme prices (£10, £50, £100) to see how the followers reacted. This proved a massive game-theory insight that the EDA missed: **Mk1, Mk2, and Mk3 DO have strong linear reaction functions!** 
Because the historical leader never explored beyond ~£1.79, their reactions were completely buried underneath daily random noise.

When the RLS Leader ran, its **Active Exploration (Days 101-105)** instantly forced the followers to reveal these hidden slopes. By Day 106, the RLS algorithm had mathematically mapped the linear reaction and spent the remaining 25 days playing the exact theoretical maximum Stackelberg equilibrium price (e.g., settling stably at ~£19.50 for Mk1 and ~£21.10 for Mk2).

**Results (Days 101-130):**
- **RLS vs Mk1:** £28531.18 Profit (Execution: ~0.049 sec)
- **RLS vs Mk2:** £31405.90 Profit (Execution: ~0.045 sec)
- **RLS vs Mk3:** £15934.41 Profit (Execution: ~0.046 sec)

**Grand Total Profit:** **£75,870**

## Positives and Negatives

### Positives
* **Extremely Profitable**: By actively exploring and calculating Stackelberg responses, it maps and perfectly exploits hidden reaction functions that baseline distribution-tracking approaches natively miss.
* **Robust to Anomalies / Outliers**: The median-filtering at initialization and daily outlier rejection (rolling $3\sigma$ threshold) means it survives massive unexpected data spikes (e.g., Mk2's historic £51 error) without crashing the model.
* **High Computational Efficiency**: Unlike polynomial solving or Bayesian updating which require iterating over large histories, RLS uses $O(1)$ matrix multiplication every day. It executes instantaneously (< 0.05 seconds).
* **Graceful Degradation**: If a Follower genuinely has no reaction function ($b=0$ slope), the Stackelberg math automatically shifts into optimizing directly against the historical mean.

### Negatives
* **Vulnerable to "Memory" Agents**: RLS strictly assumes a 1-step Markovian environment ($u_F[t]$ relies on $u_L[t-1]$). If a hidden Follower (Mk4, 5, or 6) evaluates the Leader's 5-day rolling average, or initiates multi-day "punishment" phases, the RLS will misinterpret the delayed reactions as extreme parameter drift.
* **Exploration Cost**: Deliberately charging sub-optimal bounds in Days 101-105 (e.g. dropping to £1.00) sacrifices guaranteed short-term profit in exchange for long-term mapping.
* **Linear Assumption**: If a follower has a complex quadratic, exponential, or threshold-based reaction function, the RLS will only be able to find a localized linear approximation of that curve.
