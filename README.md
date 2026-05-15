# NeuroGuard-RL

NeuroGuard-RL is a personal research project built to explore reinforcement learning in crypto trading, with a focus on risk controls, execution safety, and adversarial market behavior.

The idea is simple: the model should not be trusted blindly.  
The agent proposes actions, but the final decision still goes through a separate validation layer that checks position sizing, drawdown limits, and basic execution constraints before anything is sent to the exchange.

The project uses a custom Gymnasium environment to simulate spot trading conditions like slippage, latency, and liquidity effects. PPO from Stable-Baselines3 is used for training, with the training loop, preprocessing pipeline, and execution layer kept separate so the system is easier to test and reason about.

## What is in the repo

- `data/` for historical market data and preprocessing
- `gym_env/` for the custom trading environment
- `models/` for PPO training and saved artifacts
- `executor/` for exchange interaction and risk checks
- test scripts for data validation, simulation, and shadow execution

## Why I built it

I wanted a framework that treats trading decisions the same way I think about untrusted inputs in security work: the model can suggest something, but it should never get direct control without checks.

## Tech stack

- Stable-Baselines3
- Gymnasium
- pandas
- numpy
- pyarrow
- ccxt

## Note

This is a research project, not a production trading system. It is meant for learning, experimentation, and portfolio presentation.
