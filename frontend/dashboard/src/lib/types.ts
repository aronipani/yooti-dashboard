/**
 * Shared TypeScript interfaces for the yooti-dashboard API layer.
 */

export interface InsightAlert {
  type: string
  severity: 'warn' | 'critical' | 'info'
  message: string
  metric: string
  value: number
  threshold: number
}

export interface SprintSummary {
  sprint_num: number
  project_id: string
  cycle_time_avg_days: number
  sprint_completion_pct: number
  stories_shipped: number
  stories_committed: number
  coverage_new_code_avg: number
  regression_rate_pct: number
  escalation_rate_pct: number
  deploy_frequency: number
  agent_exec_hrs_avg: number
  human_wait_hrs_avg: number
  iteration_avg: number
  correction_rate_pct: number
  constitution_pass_pct: number
  mutation_score_avg: number
  gate_rejection_rates: Record<string, number>
  escalation_breakdown: Record<string, number>
  phase_avg_hrs: Record<string, number>
  insight_alerts: InsightAlert[]
}

export interface CurrentSnapshot extends SprintSummary {
  last_ingested_at: string
}

export interface StoryMetrics {
  story_id: string
  sprint_num: number
  type: string
  status: string
  cycle_time_hrs: number
  iteration_count: number
  escalation_type: string | null
  correction_count: number
  coverage_new_code_pct: number
  gate_timestamps: Record<string, string | null>
  phase_durations: Record<string, number> | null
  escalation_log: Array<Record<string, unknown>>
}

export interface TrendPoint {
  sprint_num: number
  value: number
  delta_from_prev: number
  direction: 'up' | 'down' | 'flat'
  metric_name: string
}

export interface SprintDetail {
  sprint_num: number
  summary: SprintSummary
  phase_avg_hrs: Record<string, number>
  gate_rejection_rates: Record<string, number>
  escalation_breakdown: Record<string, number>
  stories: StoryMetrics[]
}
