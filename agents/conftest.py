"""
Shared pytest fixtures for all agent tests.
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--eval",
        action="store_true",
        default=False,
        help="Run eval tests (requires real LLM API keys, slow)"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--eval"):
        skip_eval = pytest.mark.skip(reason="Use --eval flag to run eval tests")
        for item in items:
            if "eval" in item.keywords:
                item.add_marker(skip_eval)
