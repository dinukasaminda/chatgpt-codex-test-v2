# chatgpt-codex-test-v2

This repository contains a simple MCP server and client written in Python.
The server exposes tools that call an external HTTP service to retrieve data
about a creator's exercises and products. The client can discover the server
tools and invoke them.

## Structure

 - `server/` - FastAPI application implementing the MCP server
- `client/` - Python script that discovers and calls server tools

## Running the server

```bash
pip install -r server/requirements.txt
# Optionally set the base URL of the external service
export EXTERNAL_SERVICE_BASE_URL="https://example.com/api"
python server/app.py
```

The server will run on `http://localhost:5000` by default.

## Using the client

```bash
pip install -r client/requirements.txt
python client/client.py            # lists tools and sample prompts
python client/client.py get_exercise_list johndoe
python client/client.py get_products johndoe
```

The client first fetches available tools from the server's `/tools` endpoint,
then uses the selected tool endpoint to retrieve data.
