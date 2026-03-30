"""
DynamoDB key builders for yooti-metrics single-table design.

PK/SK patterns match ARCH-DASHBOARD.md Section 3 entity map.
All functions are pure — no I/O, no side effects.
"""


def pk(project_id: str) -> str:
    """Partition key for all entities: PROJECT#<project_id>."""
    return f"PROJECT#{project_id}"


def sk_sprint_summary(sprint_num: int) -> str:
    """Sort key for sprint summary: SPRINT#<num>#SUMMARY."""
    return f"SPRINT#{sprint_num}#SUMMARY"


def sk_story(sprint_num: int, story_id: str) -> str:
    """Sort key for story metrics: SPRINT#<num>#STORY#<story_id>."""
    return f"SPRINT#{sprint_num}#STORY#{story_id}"


def sk_phase(sprint_num: int, story_id: str) -> str:
    """Sort key for phase durations: SPRINT#<num>#PHASE#<story_id>."""
    return f"SPRINT#{sprint_num}#PHASE#{story_id}"


def sk_trend(metric_name: str, sprint_num: int) -> str:
    """Sort key for trend series: TREND#<metric_name>#SPRINT#<num>."""
    return f"TREND#{metric_name}#SPRINT#{sprint_num}"


def sk_current_snapshot() -> str:
    """Sort key for current snapshot: CURRENT#SNAPSHOT."""
    return "CURRENT#SNAPSHOT"


def sk_gate(story_id: str, gate_num: int) -> str:
    """Sort key for gate events: GATE#<story_id>#G<n>."""
    return f"GATE#{story_id}#G{gate_num}"


def sk_escalation(story_id: str, task_id: str) -> str:
    """Sort key for escalation log: ESC#<story_id>#<task_id>."""
    return f"ESC#{story_id}#{task_id}"


# Prefixes for Query begins_with operations
SK_PREFIX_SPRINT = "SPRINT#"
SK_PREFIX_TREND = "TREND#"
SK_PREFIX_GATE = "GATE#"
SK_PREFIX_ESC = "ESC#"


def sk_sprint_prefix(sprint_num: int) -> str:
    """Prefix for querying all entities in a sprint."""
    return f"SPRINT#{sprint_num}#"


def sk_story_prefix(sprint_num: int) -> str:
    """Prefix for querying all stories in a sprint."""
    return f"SPRINT#{sprint_num}#STORY#"


def sk_trend_metric_prefix(metric_name: str) -> str:
    """Prefix for querying trends for a specific metric."""
    return f"TREND#{metric_name}#"


def sk_gate_prefix(story_id: str) -> str:
    """Prefix for querying all gates for a story."""
    return f"GATE#{story_id}#"


def sk_esc_prefix(story_id: str) -> str:
    """Prefix for querying all escalations for a story."""
    return f"ESC#{story_id}#"
