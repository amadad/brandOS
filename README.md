<div align="center">
<img width="100px" src="./public/logo.png" />

# 🔍 BrandOS

### Realtime Brand Monitoring and Analysis

<p>
<img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/amadad/brandos" />
<img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/amadad/brandos" />
<img alt="GitHub Repo Size" src="https://img.shields.io/github/repo-size/amadad/brandos" />
<img alt="GitHub Stars" src="https://img.shields.io/github/stars/amadad/brandos" />
<img alt="GitHub Forks" src="https://img.shields.io/github/forks/amadad/brandos" />
<img alt="Github License" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
<img alt="Twitter" src="https://img.shields.io/twitter/follow/amadad?style=social" />
</p>
</div>

-----

<p align="center">
 <a href="#-overview">Overview</a> •
 <a href="#-features">Features</a> •
 <a href="#-prerequisites">Prerequisites</a> •
 <a href="#-installation">Installation</a> •
 <a href="#-usage">Usage</a> •
 <a href="#-functions">Functions</a> •
 <a href="#-license">License</a>
</p>

-----

**BrandOS** is a Python script that utilizes the Anthropic API and Tavily API to monitor, analyze, and suggest actions for a brand to maintain unique differentiation.

-----

## 📖 Overview

**BrandOS** contains the code and instructions needed to build a sophisticated brand monitoring and analysis tool that leverages the capabilities of [Anthropic API](https://www.anthropic.com/) and [Tavily API](https://www.tavily.com/). Designed to efficiently break down objectives into sub-tasks, generate prompts for sub-agents, and refine the results into a cohesive final output, this project is an ideal starting point for developers interested in brand management and natural language processing.

## 🎛️ Features

- Utilizes the Anthropic API for natural language processing and generation
- Integrates with the Tavily API for QnA search functionality
- Breaks down the objective into sub-tasks using an orchestrator
- Generates prompts for sub-agents to execute the sub-tasks
- Refines the sub-task results into a cohesive final output
- Provides a list of competitors, keyword search terms to monitor, and suggested actions for the brand
- Saves the full exchange log to a Markdown file

## 📋 Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Required Python packages: `os`, `re`, `json`, `dotenv`, `anthropic`, `tavily`, `rich`, `datetime`
- Anthropic API key (stored in a `.env` file as `ANTHROPIC_API_KEY`)
- Tavily API key (stored in a `.env` file as `TAVILY_API_KEY`)

## 🚀 Installation

1. Clone the repository or download the script file.

2. Install the required Python packages by running the following command:
   ```
   pip install os re json dotenv anthropic tavily rich datetime
   ```

3. Create a `.env` file in the same directory as the script and add your Anthropic and Tavily API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## 💻 Usage

1. Run the script using the following command:
   ```
   python brandos.py
   ```

2. When prompted, enter the following information about the brand:
   - Brand URL
   - Brand mission
   - Brand vision
   - Brand values

3. Choose whether you want to use search functionality by entering 'y' or 'n'.

4. The script will start the process of monitoring, analyzing, and suggesting actions for the brand. It will break down the objective into sub-tasks, generate prompts for sub-agents, and refine the results.

5. The final output will be displayed in the console, including a list of competitors, keyword search terms to monitor, and suggested actions for the brand.

6. The full exchange log will be saved to a Markdown file with a timestamp and the sanitized brand name.

## 🧩 Functions

- `calculate_subagent_cost(model, input_tokens, output_tokens)`: Calculates the cost of a sub-agent based on the model and token usage.
- `opus_orchestrator(brand_info, previous_results=None, use_search=False)`: Calls the orchestrator to break down the objective into sub-tasks and generate prompts for sub-agents.
- `haiku_sub_agent(prompt, search_query=None, previous_haiku_tasks=None, continuation=False)`: Calls the sub-agent to execute a sub-task based on the provided prompt and search query.
- `opus_refine(brand_info, sub_task_results, filename, continuation=False)`: Calls Opus to review and refine the sub-task results into a cohesive final output.

## 📄 License

**BrandOS** is open-source and licensed under [MIT](https://opensource.org/licenses/MIT).