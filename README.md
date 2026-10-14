# AI Agent (Gemini)

A simple command-line AI agent built in Python. It chats with a Google Gemini model and can use tools to get things done instead of only answering with text.

## What it does

You type a message in the terminal, and the model decides whether to answer directly or use one of its tools:

- `get_time`: returns the current date and time
- `calculate`: evaluates a math expression
- `write_note`: appends a line of text to a file in the project folder

## Setup

Requirements: Python and [uv](https://docs.astral.sh/uv/).

1. Clone the repo and open the project folder.
2. Get a free API key at [aistudio.google.com](https://aistudio.google.com).
3. Copy `.env.example` to `.env` and fill in your values:

```
   GEMINI_API_KEY=your-key-here
   GEMINI_MODEL=gemini-3.7-flash
```

4. Install dependencies:

```
   uv sync
```

## Run

```
uv run main.py
```

Type `quit` or `exit` to leave.