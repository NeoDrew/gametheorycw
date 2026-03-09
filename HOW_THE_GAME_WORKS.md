# How This Pricing Game Works — A Plain English Guide

---

## The Big Picture

Imagine you own a **petrol station**. Right across the road, there's a competitor — another petrol station. Every morning, **you put your price on the sign first**. Your competitor sees your price, thinks about it, and then sets their own price.

Whoever charges less tends to sell more. But charging too little means you make less money per litre. So you're trying to find the **sweet spot** — the price that makes you the most money, knowing your competitor will react to whatever you charge.

That's the entire game. You do this **every single day for 30 days**, and your goal is to make as much total money as possible across all 30 days.

---

## The Two Players

### You — The Leader 🏆
- You go **first**. You announce your price before anyone else.
- You know your own costs (your "unit cost" is £1 — think of it as what it costs you to produce one unit).
- You want to **maximise your total profit** over 30 days.
- Your price must always be **at least £1** (you can't sell below cost).

### Your Competitor — The Follower 👀
- They go **second**. They wait to see your price, then respond.
- You **don't know** exactly how they think or what their costs are.
- But here's the key insight: **they always respond to your price in some consistent way** — a higher price from you might make them raise theirs too, or it might not. You have to figure out their pattern.
- There are three different competitors: MK1, MK2, and MK3. Each one behaves differently.

---

## Why Does Your Competitor's Price Matter to You?

Here's the slightly counterintuitive part. You might think: "Why do I care what they charge? I just want to sell stuff."

The answer is: **your sales depend on both prices**.

Think about it like this — if your competitor charges £5 and you charge £3, customers flock to you. If you both charge £3, you split the customers. If you charge £3 and they charge £1, customers go to them.

So your sales (and therefore your profit) are affected by **the gap between your price and theirs**. The higher their price compared to yours, the more customers you get. This means you actually *want* your competitor to charge a high price — it sends customers your way.

---

## The Historical Data — Your Cheat Sheet

Before the 30-day game starts, you're given a **history book**: records of 100 previous days of this exact game being played between a leader and each follower.

Each row in this history tells you:
- What price the leader charged that day
- What price the follower responded with

This is gold. By studying these 100 days, you can start to figure out **the follower's pattern** — their "reaction function". For example, you might notice:

> *"Every time the leader charges £5, the follower charges around £4. Every time the leader charges £8, the follower charges around £6."*

Once you can predict how the follower will react to your price, you can work backwards to find the price that maximises your profit.

---

## The 30-Day Game — Day by Day

Here's exactly what happens each day during the actual game:

```
Morning:   YOU announce your price for the day
           ↓
Midday:    Your COMPETITOR sees your price and sets their own
           ↓
Evening:   You learn what your competitor charged
           ↓
Night:     You use this new info to plan tomorrow's price
```

This loop repeats 30 times.

The key thing to notice: **you learn something new every single day**. After each day, you know exactly how the follower responded to your price. A smart player uses this to constantly improve their prediction of the follower's behaviour.

---

## The Catch — Things Change

Here's what makes this hard: **the follower doesn't behave exactly the same every day**. Their situation changes — maybe their costs go up, maybe they get new stock, maybe their strategy shifts slightly. So the pattern you learned from the 100 historical days might drift a little during the 30-day game.

This means you can't just learn once at the start and coast. You need to **keep updating your understanding** of the follower as new days unfold.

---

## What "Winning" Looks Like

Your score is simply your **total profit added up across all 30 days**.

Profit on any single day = **(your price − £1) × how many units you sold**

So if you charge £4 and sell 60 units, your profit that day is:
> (£4 − £1) × 60 = **£180**

Do this for 30 days and add it all up. The higher the total, the better.

---

## The Hidden Competitors (MK4, MK5, MK6)

Here's the twist for grading: your code will also be tested against **three secret competitors** (MK4, MK5, MK6) that you've never seen before. They behave *similarly* to MK1, MK2, MK3 — but not identically.

This means your approach **cannot be tailored specifically to MK1–3**. It needs to be smart enough to adapt to a slightly different competitor on its own.

Think of it like a driving test: you practice on one car, but the examiner might put you in a slightly different model. If you genuinely learned to drive (not just memorise that car), you'll be fine.

---

## Summary in One Paragraph

You're a business owner setting prices every day, competing against a rival whose strategy you don't fully know. You go first each day, your rival reacts to your price, and both of your prices determine how much you each sell. You have 100 days of historical data to study your rival's patterns, and 30 days to actually play and make as much money as possible. The smarter you are at predicting how your rival will react — and the faster you adapt when their behaviour shifts — the more money you make.

---

*That's it. Everything else in the coursework is just the maths and code to do this systematically.*
