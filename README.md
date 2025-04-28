# Personal Finance Multi-Agent Portal

This project is a multi-agent personal finance management portal designed to help users manage their spending, investments, and projects through intelligent, autonomous agents.

## Key Features

- **Spend Management Agent**
  - Categorizes transactions based on user taxonomy
  - Tracks and alerts on budget usage
  - Manages and reminds about bills

- **Investment Management Agent**
  - Tracks portfolio returns
  - Detects underperforming funds
  - Proposes reallocations

- **Project Management Agent**
  - Evaluates project NPVs, IRRs, VPN
  - Optimizes debt repayment schedules
  - Compares multiple project alternatives

## Architecture Overview

The portal uses:
- OpenAI's Agents SDK for orchestration
- Python-based custom tools
- Lightweight session memory for user context
- Chain-of-thought reasoning before action selection

## Getting Started

### Requirements

Install required Python packages:

```bash
pip install -r requirements.txt
```

### Running the Portal

```bash
python main.py
```

Ensure you have set your OpenAI API Key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```
Or on Windows CMD:

```bash
set OPENAI_API_KEY=your-api-key
```

### Folder Structure

```
main.py
/my_agents/           # Agents (Spend, Investment, Project)
/tools/               # Tools (classifiers, calculators, optimizers)
/requirements.txt     # Required Python packages
/README.md            # This file
```

## Future Extensions

- Market sentiment analysis for stock investments
- Full bill payment tracking and forecasting
- Auto-rebalancing portfolio strategies
- Financial health dashboard

