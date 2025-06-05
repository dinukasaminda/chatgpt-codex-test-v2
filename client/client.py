import argparse
import requests

DEFAULT_SERVER = 'http://localhost:5000'


def discover_tools(server_url: str):
    resp = requests.get(f"{server_url}/tools")
    resp.raise_for_status()
    return resp.json()


def call_tool(server_url: str, tool_endpoint: str, params: dict):
    resp = requests.get(f"{server_url}{tool_endpoint}", params=params)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="MCP Client")
    parser.add_argument('--server', default=DEFAULT_SERVER, help='MCP server URL')
    parser.add_argument('command', nargs='?', help='Tool command to run')
    parser.add_argument('username', nargs='?', help='Creator username')
    args = parser.parse_args()

    tools_info = discover_tools(args.server)
    print("Available tools:")
    for name, info in tools_info['tools'].items():
        print(f"- {name}: {info['description']} -> {info['endpoint']}")
    print("Sample prompts:")
    for prompt in tools_info['sample_prompts']:
        print(f"  * {prompt}")

    if args.command and args.username:
        tool = tools_info['tools'].get(args.command)
        if not tool:
            print(f"Unknown command {args.command}")
            return
        result = call_tool(args.server, tool['endpoint'], {'username': args.username})
        print("Result:")
        print(result)


if __name__ == '__main__':
    main()
