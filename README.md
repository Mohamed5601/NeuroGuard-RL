# NeuroGuard-RL

NeuroGuard-RL is a personal research project built to explore reinforcement learning in crypto spot trading.

The main idea is simple: the model can suggest an action, but it should not be trusted blindly. Before anything reaches execution, the decision goes through a separate risk layer that checks basic constraints like position sizing, drawdown limits, and other safety rules.

I built this project to study a few things at the same time:
- how RL behaves in noisy market conditions
- how to keep model output separate from execution logic
- how to add simple invariant checks around trading decisions
- how to make the whole system easier to test and reason about

## What is inside

- `data/` for historical market data, preprocessing, and feature extraction
- `gym_env/` for the custom Gymnasium trading environment
- `models/` for PPO training and saved artifacts
- `executor/` for exchange connection, order handling, and risk checks
- test scripts for data validation, simulation, and shadow execution

## How it works

The project models spot trading as a Markov Decision Process and uses PPO from Stable-Baselines3 to train an agent inside a custom environment.

That environment tries to stay close to real conditions by including things like:
- fees
- slippage
- latency
- liquidity constraints

The training code, the preprocessing pipeline, and the execution layer are kept separate on purpose. I found this easier to debug, easier to test, and less likely to turn into a mess later.

## Why I made it this way

Coming from a security background, I like systems that do not trust inputs too early.

In this case, the model is just another input source. It can help, but it should never get direct control over execution without checks.

## Tech stack

- Stable-Baselines3
- Gymnasium
- pandas
- numpy
- pyarrow
- ccxt

## Project Status

This repository is still experimental and under active development.

Some parts of the codebase were written quickly during testing and research iterations, so the structure and comments are not fully standardized yet.

The goal of the project was mainly to experiment with reinforcement learning workflows, execution safety, and modular trading system design rather than build a production-ready platform.

## Future Ideas

One direction I would like to explore later is combining the current execution framework with a higher-level LLM-based system for market interpretation and strategy adaptation.

The idea would be to keep execution and risk validation isolated while using language models for slower decision-making tasks like:
- market regime analysis
- news interpretation
- sentiment monitoring
- dynamic strategy adjustments

For now, the focus of this repository is still on the lower-level execution and reinforcement learning infrastructure.

## Note

This is a research repo, not a production trading system. It is meant for learning, experimentation, and portfolio presentation.
