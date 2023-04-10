# IMDB-LLM: Movie Query Made Simple

![IMDB-LLM Demo](./image/llm-imdb.gif)

Welcome to IMDB-LLM, a proof of concept app that demonstrates the power of [LangChain](https://github.com/hwchase17/langchain) and LLMs in extracting information from graphs! In just 10 hours it is possible to develop a user-friendly application that enables users to search for movie titles in the IMDB dataset graph or discover similar movies using natural language queries. The best part? If the LLM lacks specific information, it will first search on Google, then query the title in the database.

## Overview

IMDB-LLM's Graph Explorer is built using [LangChain](https://github.com/hwchase17/langchain) and LLMs, state-of-the-art technologies in natural language processing and machine learning. The application employs a graph representation of the IMDB dataset, encompassing data on movies, actors, directors, and more. Users can input queries in natural language, such as "Give me some drama movie options with Leonardo DiCaprio" or "Show me movies directed by Christopher Nolan", and the LLM will retrieve the pertinent information from the graph.

Should the LLM be unable to provide an answer, it will utilize the Google Search API to find supplementary information, which it will then use to refine the search.

## Features

- Search for movie titles within the graph
- Discover similar movies using natural language queries
- Automatic Google search for missing information

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/ibiscp/LLM-IMDB.git

```

2. Navigate to the frontend directory and install the required dependencies

```bash
cd frontend
npm install
```

3. Install the necessary dependencies for the backend

```bash
poetry install
```

4. Launch the frontend

```bash
npm run start
```

5. Set up the environment variables

```bash
export OPENAI_API_KEY=<your-openai-api-key>
export SERPAPI_API_KEY=<your-serpapi-api-key>
```

6. Start the backend

```bash
python3 backend/main.py
```

7. Open the application in your browser at http://localhost:3000
