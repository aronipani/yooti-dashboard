# Architecture — Yooti Dashboard

> Full architecture document. See README.md for overview.

## Status
This document covers the completed Sprint 1 architecture.
Sprint 2 (Terraform deployment) will add infra/ architecture.

## Key decisions made at Gate G2

### DASH-001 — FilterExpression annotation
FilterExpression must use Attr("SK").contains("#SUMMARY")
to avoid full table scans. Applied in T002.

### DASH-006 — TTL annotation
MetricsTable must include TimeToLiveSpecification
with ttl attribute. Applied in T001.

## DynamoDB access patterns
See README.md for the full single-table design.

## Lambda handler design
See services/api_python/src/handlers/ for all 6 handlers.

## SAM template
See template.yaml for the full resource definition.
