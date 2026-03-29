#!/usr/bin/env python3
"""
Invoke a Lambda handler locally against LocalStack.
Edit the EVENT dict to match your use case.

Usage:
    python scripts/invoke_local.py
    python scripts/invoke_local.py --handler src.handlers.my_handler
"""
import argparse
import importlib
import json
import os
import sys
from dotenv import load_dotenv

# Load .env — sets AWS_ENDPOINT_URL to point at LocalStack
load_dotenv()

# Default test event — edit this to match your handler's input
EVENT = {
    "httpMethod": "POST",
    "path": "/items",
    "pathParameters": None,
    "queryStringParameters": None,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({
        "name": "test-item",
        "value": 42,
    }),
    "isBase64Encoded": False,
}


class LocalContext:
    """Minimal Lambda context object for local testing."""
    function_name    = "yooti-dashboard-local"
    memory_limit_in_mb = 128
    aws_request_id   = "local-invoke-001"
    invoked_function_arn = "arn:aws:lambda:us-east-1:000000000000:function:yooti-dashboard"
    def get_remaining_time_in_millis(self): return 30000


def invoke(handler_path: str, event: dict):
    module_path, func_name = handler_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    handler_func = getattr(module, func_name)

    print(f"Invoking {handler_path}")
    print(f"Endpoint: {os.environ.get('AWS_ENDPOINT_URL', 'real AWS')}")
    print(f"Event: {json.dumps(event, indent=2)}\n")

    response = handler_func(event, LocalContext())

    print(f"Status:  {response.get('statusCode')}")
    try:
        body = json.loads(response.get("body", "{}"))
        print(f"Body:\n{json.dumps(body, indent=2)}")
    except Exception:
        print(f"Body: {response.get('body')}")
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--handler", default="src.handlers.create_item.handler",
                        help="Python module path to handler function")
    parser.add_argument("--event", help="Path to JSON event file")
    args = parser.parse_args()

    event = EVENT
    if args.event:
        with open(args.event) as f:
            event = json.load(f)

    invoke(args.handler, event)
