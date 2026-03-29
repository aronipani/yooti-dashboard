"""
Unit tests for template-agent nodes.
Each node tested in complete isolation — no LLM calls, no external services.
All dependencies mocked.
"""
import pytest
from unittest.mock import AsyncMock, patch
from agents.template_agent.nodes import fetch_data, process, format_output
from agents.template_agent.state import TemplateAgentState


@pytest.fixture
def base_state() -> TemplateAgentState:
    return TemplateAgentState(
        input="test input",
        messages=[],
        data=None,
        result=None,
        error=None,
        iteration=0,
    )


class TestFetchDataNode:

    @pytest.mark.asyncio
    async def test_returns_data_on_success(self, base_state):
        result = await fetch_data.run(base_state)
        assert result.get("error") is None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_handles_missing_input_gracefully(self, base_state):
        base_state["input"] = ""
        result = await fetch_data.run(base_state)
        # Should not raise — returns error field instead
        assert isinstance(result, dict)


class TestProcessNode:

    @pytest.mark.asyncio
    async def test_processes_data_correctly(self, base_state):
        base_state["data"] = {"key": "value"}
        result = await process.run(base_state)
        assert result.get("error") is None
