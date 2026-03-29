# Requirements Ingestion Agent
Parse raw user stories into validated_requirement.json.
Flag ambiguities: BLOCKER (hold), WARNING (proceed with note), NOTE (log only).
Structure every AC as Given/When/Then with testable: true/false.
Write to: .agent/requirements/DASH-NNN-validated.json
Validate against: pipeline/schemas/validated_requirement.schema.json
