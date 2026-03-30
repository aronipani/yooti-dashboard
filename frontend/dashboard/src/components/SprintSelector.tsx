/**
 * SprintSelector — dropdown to pick a sprint from the sprint list.
 * Shows loading skeleton, error state with retry, and sprint numbers descending.
 */
import React from 'react'
import { useSprintList } from '../lib/hooks'

export interface SprintSelectorProps {
  projectId: string
  value: number | null
  onChange: (sprintNum: number) => void
}

export function SprintSelector({
  projectId,
  value,
  onChange,
}: SprintSelectorProps): React.ReactElement {
  const { data: sprints, isLoading, isError, refetch } = useSprintList(projectId)

  if (isLoading) {
    return (
      <div data-testid="sprint-selector-loading" role="status" aria-label="Loading sprints">
        <span className="block h-10 w-48 animate-pulse rounded bg-gray-200" />
      </div>
    )
  }

  if (isError) {
    return (
      <div data-testid="sprint-selector-error" role="alert">
        <p>Failed to load sprints.</p>
        <button
          type="button"
          onClick={() => { void refetch() }}
          aria-label="Retry loading sprints"
        >
          Retry
        </button>
      </div>
    )
  }

  const sorted = [...(sprints ?? [])].sort(
    (a, b) => b.sprint_num - a.sprint_num
  )

  return (
    <label>
      <span className="sr-only">Select sprint</span>
      <select
        data-testid="sprint-selector"
        value={value ?? ''}
        onChange={(e) => {
          const num = Number(e.target.value)
          if (!Number.isNaN(num)) {
            onChange(num)
          }
        }}
        aria-label="Select sprint"
      >
        <option value="" disabled>
          Choose a sprint
        </option>
        {sorted.map((s) => (
          <option key={s.sprint_num} value={s.sprint_num}>
            Sprint {s.sprint_num}
          </option>
        ))}
      </select>
    </label>
  )
}
