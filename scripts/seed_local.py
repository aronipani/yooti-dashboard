"""Seed LocalStack DynamoDB with test dashboard data."""
import boto3
from datetime import datetime
from decimal import Decimal

endpoint = "http://localhost:4566"
table_name = "yooti-metrics"
project_id = "yooti-dashboard"
pk = f"PROJECT#{project_id}"
now = datetime.utcnow().isoformat() + "Z"

ddb = boto3.resource(
    "dynamodb",
    endpoint_url=endpoint,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
table = ddb.Table(table_name)


def d(val):
    """Convert float to Decimal for DynamoDB."""
    if isinstance(val, float):
        return Decimal(str(val))
    if isinstance(val, dict):
        return {k: d(v) for k, v in val.items()}
    if isinstance(val, list):
        return [d(v) for v in val]
    return val


# Sprint 1 summary
table.put_item(Item=d({
    "PK": pk, "SK": "SPRINT#1#SUMMARY",
    "project_id": project_id, "sprint_num": 1,
    "cycle_time_avg_days": 3.2, "sprint_completion_pct": 78,
    "stories_shipped": 7, "stories_committed": 9,
    "coverage_new_code_avg": 89, "regression_rate_pct": 2,
    "escalation_rate_pct": 11, "deploy_frequency": 3,
    "agent_exec_hrs_avg": 2.1, "human_wait_hrs_avg": 5.4,
    "iteration_avg": 3.1, "correction_rate_pct": 15,
    "constitution_pass_pct": 96, "mutation_score_avg": 72,
    "gate_rejection_rates": {"G2": 10, "G3": 5},
    "escalation_breakdown": {"SCOPE_ERROR": 3, "ENV_ERROR": 2, "SPEC_AMBIGUITY": 1},
    "phase_avg_hrs": {"requirements": 2, "planning": 3, "coding": 12, "review": 4},
    "insight_alerts": [
        {"type": "BOTTLENECK", "severity": "warn", "message": "Coding phase averaging 12h", "metric": "phase_avg_hrs.coding", "value": 12, "threshold": 8},
        {"type": "ESCALATION_SPIKE", "severity": "critical", "message": "Escalation rate 11% above threshold", "metric": "escalation_rate_pct", "value": 11, "threshold": 10},
    ],
    "updated_at": now,
}))

# Sprint 2 summary
table.put_item(Item=d({
    "PK": pk, "SK": "SPRINT#2#SUMMARY",
    "project_id": project_id, "sprint_num": 2,
    "cycle_time_avg_days": 2.1, "sprint_completion_pct": 90,
    "stories_shipped": 9, "stories_committed": 10,
    "coverage_new_code_avg": 92, "regression_rate_pct": 0,
    "escalation_rate_pct": 5, "deploy_frequency": 4,
    "agent_exec_hrs_avg": 1.3, "human_wait_hrs_avg": 3.2,
    "iteration_avg": 2.4, "correction_rate_pct": 8,
    "constitution_pass_pct": 100, "mutation_score_avg": 80,
    "gate_rejection_rates": {"G2": 5, "G3": 0},
    "escalation_breakdown": {"SCOPE_ERROR": 1},
    "phase_avg_hrs": {"requirements": 1, "planning": 2, "coding": 8, "review": 3},
    "insight_alerts": [],
    "updated_at": now,
}))

# Current snapshot (latest sprint)
table.put_item(Item=d({
    "PK": pk, "SK": "CURRENT#SNAPSHOT",
    "project_id": project_id, "sprint_num": 2,
    "cycle_time_avg_days": 2.1, "sprint_completion_pct": 90,
    "stories_shipped": 9, "stories_committed": 10,
    "coverage_new_code_avg": 92, "regression_rate_pct": 0,
    "escalation_rate_pct": 5, "deploy_frequency": 4,
    "agent_exec_hrs_avg": 1.3, "human_wait_hrs_avg": 3.2,
    "iteration_avg": 2.4, "correction_rate_pct": 8,
    "constitution_pass_pct": 100, "mutation_score_avg": 80,
    "gate_rejection_rates": {"G2": 5, "G3": 0},
    "escalation_breakdown": {"SCOPE_ERROR": 1},
    "phase_avg_hrs": {"requirements": 1, "planning": 2, "coding": 8, "review": 3},
    "insight_alerts": [
        {"type": "QUALITY_DROP", "severity": "info", "message": "Mutation score 80% — approaching 85% target", "metric": "mutation_score_avg", "value": 80, "threshold": 85},
    ],
    "last_ingested_at": now,
    "updated_at": now,
}))

# Stories for sprint 2
stories = [
    {"story_id": "DASH-001", "type": "feature", "status": "complete", "cycle_time_hrs": 14, "iteration_count": 3, "escalation_type": None, "correction_count": 1, "coverage_new_code_pct": 95},
    {"story_id": "DASH-002", "type": "feature", "status": "complete", "cycle_time_hrs": 10, "iteration_count": 2, "escalation_type": None, "correction_count": 0, "coverage_new_code_pct": 92},
    {"story_id": "DASH-003", "type": "feature", "status": "complete", "cycle_time_hrs": 6, "iteration_count": 1, "escalation_type": None, "correction_count": 0, "coverage_new_code_pct": 90},
    {"story_id": "DASH-004", "type": "feature", "status": "complete", "cycle_time_hrs": 12, "iteration_count": 2, "escalation_type": None, "correction_count": 1, "coverage_new_code_pct": 91},
    {"story_id": "DASH-005", "type": "feature", "status": "complete", "cycle_time_hrs": 16, "iteration_count": 3, "escalation_type": "SCOPE_ERROR", "correction_count": 2, "coverage_new_code_pct": 88},
    {"story_id": "DASH-006", "type": "feature", "status": "complete", "cycle_time_hrs": 4, "iteration_count": 1, "escalation_type": None, "correction_count": 0, "coverage_new_code_pct": 100},
    {"story_id": "DASH-007", "type": "feature", "status": "complete", "cycle_time_hrs": 11, "iteration_count": 2, "escalation_type": None, "correction_count": 0, "coverage_new_code_pct": 93},
    {"story_id": "DASH-008", "type": "feature", "status": "complete", "cycle_time_hrs": 8, "iteration_count": 2, "escalation_type": None, "correction_count": 0, "coverage_new_code_pct": 94},
    {"story_id": "DASH-009", "type": "feature", "status": "in_progress", "cycle_time_hrs": 20, "iteration_count": 4, "escalation_type": None, "correction_count": 1, "coverage_new_code_pct": 87},
]

for s in stories:
    table.put_item(Item=d({
        "PK": pk,
        "SK": f"SPRINT#2#STORY#{s['story_id']}",
        "project_id": project_id,
        "sprint_num": 2,
        **s,
        "gate_timestamps": {"G1": "2026-03-25T10:00:00Z", "G2": "2026-03-26T14:00:00Z", "G3": None},
        "phase_durations": {"requirements": 1, "planning": 2, "coding": int(s["cycle_time_hrs"] * 0.6), "review": int(s["cycle_time_hrs"] * 0.2)},
        "escalation_log": [{"type": s["escalation_type"], "task_id": "T001", "timestamp": now}] if s["escalation_type"] else [],
        "updated_at": now,
    }))

# Trend points across sprints
metrics = {
    "cycle_time_avg_days": [3.2, 2.1],
    "sprint_completion_pct": [78, 90],
    "stories_shipped": [7, 9],
    "stories_committed": [9, 10],
    "coverage_new_code_avg": [89, 92],
    "deploy_frequency": [3, 4],
    "escalation_rate_pct": [11, 5],
}

for metric, values in metrics.items():
    for sprint_num, value in enumerate(values, 1):
        table.put_item(Item=d({
            "PK": pk,
            "SK": f"TREND#{metric}#SPRINT#{sprint_num}",
            "project_id": project_id,
            "metric_name": metric,
            "sprint_num": sprint_num,
            "value": value,
            "updated_at": now,
        }))

print("Seeded successfully:")
print("  2 sprint summaries")
print("  1 current snapshot")
print("  9 stories (sprint 2)")
print("  14 trend points (7 metrics x 2 sprints)")
print("  Total: 26 items")
