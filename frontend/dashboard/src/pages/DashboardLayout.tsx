/**
 * DashboardLayout — top-level layout with tab navigation and sprint selector.
 * Manages active tab state, project ID, and selected sprint.
 */
import { useState } from 'react'
import { clsx } from 'clsx'
import { SprintSelector } from '../components/SprintSelector'
import { ProductivityTab } from './ProductivityTab'
import { QualityTab } from './QualityTab'
import { AgentEfficiencyTab } from './AgentEfficiencyTab'
import { ValueTab } from './ValueTab'
import { DoraTab } from './DoraTab'
import { StoryDrilldownTab } from './StoryDrilldownTab'

const PROJECT_ID = import.meta.env.VITE_PROJECT_ID ?? 'yooti-dashboard'

const TABS = [
  { id: 'productivity', label: 'Productivity' },
  { id: 'quality', label: 'Quality' },
  { id: 'agent-efficiency', label: 'Agent Efficiency' },
  { id: 'value', label: 'Value' },
  { id: 'dora', label: 'DORA' },
  { id: 'story-drilldown', label: 'Story Drill-down' },
] as const

type TabId = (typeof TABS)[number]['id']

export function DashboardLayout() {
  const [activeTab, setActiveTab] = useState<TabId>('productivity')
  const [selectedSprint, setSelectedSprint] = useState<number | null>(null)

  function renderActiveTab() {
    switch (activeTab) {
      case 'productivity':
        return <ProductivityTab projectId={PROJECT_ID} />
      case 'quality':
        return <QualityTab projectId={PROJECT_ID} />
      case 'agent-efficiency':
        return <AgentEfficiencyTab projectId={PROJECT_ID} />
      case 'value':
        return <ValueTab projectId={PROJECT_ID} />
      case 'dora':
        return <DoraTab projectId={PROJECT_ID} />
      case 'story-drilldown':
        return <StoryDrilldownTab projectId={PROJECT_ID} selectedSprint={selectedSprint} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h1 className="text-xl font-bold text-gray-900">Yooti Dashboard</h1>
            <SprintSelector
              projectId={PROJECT_ID}
              value={selectedSprint}
              onChange={setSelectedSprint}
            />
          </div>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="border-b border-gray-200 bg-white" aria-label="Dashboard tabs">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="-mb-px flex flex-col md:flex-row md:space-x-6" role="tablist">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`tabpanel-${tab.id}`}
                id={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  'whitespace-nowrap border-b-2 px-1 py-3 text-sm font-medium transition-colors',
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Tab content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div
          role="tabpanel"
          id={`tabpanel-${activeTab}`}
          aria-labelledby={`tab-${activeTab}`}
        >
          {renderActiveTab()}
        </div>
      </main>
    </div>
  )
}
