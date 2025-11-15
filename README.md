# Building Eval-Driven AI Agents

A hands-on workshop teaching systematic AI agent development using evaluation-driven methodologies with **Microsoft Agents Framework** and **Azure AI Evaluation SDK**.

## Overview

This workshop demonstrates how to build production-ready AI agents that handle real-world tasks beyond simple chat.

Using a campus event management system as the use case, you'll learn to create agents with multiple tools, evaluate their performance systematically, and improve them based on metrics.

## Workshop Structure

### Lab 0: Environment Setup

- Install Microsoft Agents Framework
- Configure GitHub Models for free LLM access
- Deploy mock backend API with ngrok
- Test the complete setup

### Lab 1: Building the Agent

Build a campus event agent with 4 tools:

- **Browse events** - List all available campus events
- **Get details** - Retrieve information about specific events  
- **Register students** - Sign up for events
- **View participants** - Check who's registered

**Key concepts:**

- Defining tools with type hints and auto-generated schemas
- Creating agents with Microsoft Agents Framework
- Multi-turn conversations with thread management
- Mixing READ and WRITE operations

### Lab 2: Evaluation & Improvement

Systematically evaluate and improve agent performance:

- Create structured test datasets
- Use Azure AI evaluators (Relevance, Task Adherence)
- Build custom code-based evaluators (Conciseness)
- Measure baseline performance
- Improve based on identified issues
- Quantify improvements

**Evaluation workflow:**

1. Create tests (evaluation dataset)
2. Measure baseline (current performance)
3. Improve (fix identified issues)
4. Re-measure (verify improvement)

## Project Structure

```text
├── backend/
│   └── mock_backend.py       # FastAPI backend with event, venue & notification APIs
├── labs/
│   ├── Lab0_Setup.ipynb      # Environment setup
│   ├── Lab1_Building_Agent.ipynb  # Agent development
│   ├── Lab2_Evaluation.ipynb # Evaluation & improvement
│   └── utils.py              # Helper functions for schema generation & tracing
└── README.md
```

## Prerequisites

- Python 3.8+
- GitHub account (for GitHub Models free tier)
- ngrok account (for exposing local backend)
- Google Colab (recommended) or local Jupyter environment

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/tezansahu/building-eval-driven-ai-agents.git
   cd building-eval-driven-ai-agents
   ```

2. **Open Lab 0 in Google Colab** and follow setup instructions

3. **Complete Labs 1 & 2** sequentially

## Key Technologies

- **[Microsoft Agents Framework](https://github.com/microsoft/agent-framework)** - High-level agent orchestration
- **[Azure AI Evaluation SDK](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk)** - Systematic agent evaluation
- **[GitHub Models](https://github.com/marketplace/models)** - Free LLM access (GPT-4o-mini)
- **FastAPI** - Mock backend API
- **ngrok** - Public URL for backend

## Learning Outcomes

After completing this workshop, you will:

- ✅ Build agents with multiple tools (GET and POST operations)
- ✅ Auto-generate tool schemas from type-hinted functions
- ✅ Manage multi-turn conversations with threads
- ✅ Create evaluation datasets for agent testing
- ✅ Use Azure AI evaluators and build custom ones
- ✅ Measure and quantify agent improvements
- ✅ Apply evaluation-driven development to AI agents

## Extending the Workshop

The mock backend includes additional endpoints for:

- **Venue Management** - Check availability, book venues
- **Notifications** - Send announcements to participants

Try building agents for these domains using the same patterns!

## License

MIT

## Author

**Tezan Sahu** - Workshop materials developed for hands-on AI agent development training

## Workshop

"Beyond Chat - Building Eval-Driven AI Agents"

