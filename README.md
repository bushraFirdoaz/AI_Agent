# Multi-Step AI Agent

## Overview

A local AI agent built using **Python, LangGraph, Ollama, and Llama 3.2**.

The agent understands the user's request, decides what action is needed, uses the appropriate tool, and generates the final response.

It is integrated with **FastAPI** and **Open WebUI** to provide a chat-based interface.

## Features

- Multi-step agent workflow using LangGraph
- Calculator tool for mathematical queries
- Date & Time tool
- Weather tool
- Conditional routing and state management
- Error handling
- Local LLM using Ollama + Llama 3.2
- FastAPI OpenAI-compatible API
- Open WebUI integration

## Architecture

```text
User
 ↓
Open WebUI
 ↓
FastAPI
 ↓
LangGraph Agent
 ↓
Routing
 ├── Calculator
 ├── Date & Time
 ├── Weather
 └── General Question
 ↓
Ollama + Llama 3.2
 ↓
Final Response

UseCase_agent/
│
├── src/
│   ├── api.py
│   ├── graph.py
│   ├── main.py
│   ├── nodes.py
│   ├── prompts.py
│   └── state.py
│
├── tools/
│   ├── calculator.py
│   ├── datetime_tool.py
│   └── weather.py
│
├── UI/
│   └── app.py
│
├── requirements.txt
└── README.md

How It Works
1. User enters a question in Open WebUI.
2. Open WebUI sends the request to the FastAPI server.
3. FastAPI calls run_agent().
4. LangGraph manages the agent workflow and routing.
5. The required tool is executed when needed.
6. Ollama runs Llama 3.2 for language understanding and response generation.
7. The final answer is returned to Open WebUI.
Technologies
- Python
- LangGraph
- Ollama
- Llama 3.2
- FastAPI
- Open WebUI
Run Locally
1. Install dependencies
pip install -r requirements.txt

2. Start Ollama
ollama pull llama3.2

3. Run the agent
python -m src.main

4. Run the FastAPI server
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000

5. Open WebUI
Open:
http://localhost:8080

Connect the agent using:
http://127.0.0.1:8000/v1

Model ID:
my-ai-agent

Example
User: What is 25 * 8?
Agent: 200

User: What is temperature in Hyderabad right now and what is 10% of it?
Agent: Temperature in Hyderabad is 32.7 degrees celsius. 10% of 32.7 is 3.27
