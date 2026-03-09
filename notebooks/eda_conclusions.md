# Exploratory Data Analysis: Follower Profiles & Key Findings

This document summarises the numerical findings from the 100-day historical data for followers Mk1, Mk2, and Mk3. The primary goal of this analysis was to understand their pricing behaviour, volatility, and relationship to the leader's price.

---

## 1. Follower Mk1 Profile

Mk1 behaves as a noisy, highly volatile competitor that maintains a high price point. It shows absolutely no strong linear dependence on our price.

### Key Metrics
- **Mean Price:** £3.51
- **Standard Deviation:** £0.18
- **Price Range [min, max]:** [£3.09, £3.99]
- **Correlation with Leader ($r_{u_L, u_F}$):** +0.40
- **Lag-1 Autocorrelation ($r_{u_F[t], u_F[t-1]}$):** -0.06

### Behavioural Insights
1. **High Baseline Pricing:** Mk1 consistently prices much higher than the historical leader (~£3.51 vs ~£1.79).
2. **Weak Leader Dependence:** While there is a slight positive correlation (0.40) with the leader's price, it is extremely noisy. Linear regression yields an $R^2$ of just 0.16. Mk1 does not systematically match or linearly undercut the leader.
3. **No Temporal Drift:** The rolling 20-day mean stays remarkably stable between £3.45 and £3.55.
4. **No Autocorrelation:** The negative lag-1 autocorrelation (-0.06) suggests Mk1's price bounces "randomly" day-to-day rather than smoothly drifting or trending. It does not look at its own past prices.

---

## 2. Follower Mk2 Profile

Mk2 is an extremely stable, static competitor that occasionally executes massive, erratic "test" spikes.

### Key Metrics (Clean Data, excluding Day 35 outlier)
- **Mean Price:** £2.45
- **Standard Deviation:** £0.46
- **Price Range [min, max]:** [£1.47, £3.52] (excluding outlier)
- **Correlation with Leader ($r_{u_L, u_F}$):** +0.11
- **Lag-1 Autocorrelation ($r_{u_F[t], u_F[t-1]}$):** -0.01

### The Day 35 Outlier
On Day 35, Mk2's price spiked to **£51.78**. 
- This outlier completely destroys standard Least Squares ($R^2$ drops to 0.008).
- It suggests Mk2 might have hard-coded "exploration" days or bounds-testing mechanics where it drastically alters its price regardless of the environment.

### Behavioural Insights
1. **Practically Constant:** Ignoring the outlier, Mk2 acts like a flat line. The correlation with the leader's price is a negligible 0.11. 
2. **Dangers of Outliers:** Any tracking model must include robust outlier rejection (e.g., median filtering or clipping), otherwise the Day 35 spike will catastrophically alter predictions.
3. **No Drift:** The rolling mean of Mk2 is completely flat around £2.45.

---

## 3. Follower Mk3 Profile

Mk3 is a low-priced, highly constrained competitor. It operates tightly near the cost floor.

### Key Metrics
- **Mean Price:** £1.34
- **Standard Deviation:** £0.07
- **Price Range [min, max]:** [£1.23, £1.58]
- **Strategy Space Limit:** Remainder of the project manual limits Mk3/Mk6 leader responses to `[1.0, 15.0]`.
- **Correlation with Leader ($r_{u_L, u_F}$):** +0.19
- **Lag-1 Autocorrelation ($r_{u_F[t], u_F[t-1]}$):** +0.02

### Behavioural Insights
1. **Aggressive Pricing:** Mk3 averages £1.34, making it the most aggressive competitor. It keeps margins razor-thin compared to the £1.00 cost limit.
2. **Tight Variance:** With a standard deviation of just £0.07, Mk3 is the most predictable follower. 
3. **Weak Leader Dependence:** With a correlation of just 0.19 ($R^2$ = 0.04), Mk3 ignores the leader almost completely, sticking to its narrow, low-priced band. 

---

## The Exploration Fallacy: Colab Probe Discoveries

The initial EDA on the 100-day historical data suggested that the followers behaved as independent random variables. However, this was an **illusion caused by poor historical exploration**. 

The historical leader priced in an extremely narrow band (averaging £1.79). Because the variance in $u_L$ was so small, the linear reaction $b \cdot u_L$ was completely dwarfed by the followers' daily noise ($\pm £0.20$ to $£0.50$). 

To test this, a "Probe Leader" was built and run in the live Colab Engine (Days 101-110), deliberately injecting extreme prices (£10, £25, £50, £100) to force the followers out of their local noise band. 

### The True Hidden Reaction Functions
The probe conclusively proved that **all three followers possess strong linear reaction functions**:

*   **Mk1 Reaction:** $u_F = 2.02 + 0.75 \cdot u_L \quad (R^2 = 0.998)$
    *   *Proof:* When probed with £100, Mk1 priced at £78.78.
*   **Mk2 Reaction:** $u_F = 1.63 + 0.81 \cdot u_L \quad (R^2 = 1.000)$
    *   *Proof:* When probed with £100, Mk2 priced at £83.30.
*   **Mk3 Reaction:** $u_F = 1.92 + 0.04 \cdot u_L \quad (R^2 = 0.668)$
    *   *Proof:* When probed with £100, Mk3 priced at £5.36.

### Memory / Temporal Lag Probe
A subsequent Memory Probe tested whether the followers exhibited multi-day memory or grudges (e.g., maintaining high prices after the £100 spike). 
The results proved that **Mk1, Mk2, and Mk3 are purely 1-step Markovian agents**. The very next turn after a £100 shock, all three instantly returned to their lowest baseline (£2-3). They have zero memory of past prices beyond $t-1$.

## Final Conclusion & Strategic Implications

The historical data is deceptive. Followers Mk1, Mk2, and Mk3 are NOT random noise generators; they are strictly mathematical 1-step linear respondents. 

**Strategic Implications:**
1.  **Exploration is Mandatory:** Any successful advanced agent must deliberately explore the price space in the early live game to force the hidden parameters ($a$ and $b$) out of the noise floor.
2.  **RLS is Optimal:** Because the followers have zero memory and a strong linear response, a 1-Step Recursive Least Squares (RLS) tracking algorithm is mathematically perfectly suited to map them and calculate the Stackelberg optimal response.
3.  **Outlier Protection:** Mk2's historic £51 spike remains a genuine anomaly. The RLS model must still deploy active outlier rejection to prevent model collapse during random environment shocks.
