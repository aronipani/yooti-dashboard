/**
 * DashboardLayout — top-level layout with tab navigation and sprint selector.
 * Manages active tab state and renders the corresponding tab page.
 */
import { useState } from 'react'
import { clsx } from 'clsx'
import { ProductivityTab } from './ProductivityTab'
import { QualityTab } from './QualityTab'
import { AgentEfficiencyTab } from './AgentEfficiencyTab'
import { ValueTab } from './ValueTab'
import { DoraTab } from './DoraTab'
import { StoryDrilldownTab } from './StoryDrilldownTab'

const TABS = [
  { id: 'productivity', label: 'Productivity' },
  { id: 'quality', label: 'Quality' },
  { id: 'agent-efficiency', label: 'Agent Efficiency' },
  { id: 'value', label: 'Value' },
  { id: 'dora', label: 'DORA' },
  { id: 'story-drilldown', label: 'Story Drill-down' },
] as const

type TabId = (typeof TABS)[number]['id']

const TAB_COMPONENTS: Record<TabId, React.ComponentType> = {
  productivity: ProductivityTab,
  quality: QualityTab,
  'agent-efficiency': AgentEfficiencyTab,
  value: ValueTab,
  dora: DoraTab,
  'story-drilldown': StoryDrilldownTab,
}

export function DashboardLayout() {
  const [activeTab, setActiveTab] = useState<TabId>('productivity')

  const ActiveComponent = TAB_COMPONENTS[activeTab]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h1 className="text-xl font-bold text-gray-900">Yooti Dashboard</h1>
            {/* Sprint selector placeholder — will be connected to hooks later */}
            <div className="flex items-center gap-2">
              <label htmlFor="sprint-selector" className="text-sm font-medium text-gray-600">
                Sprint:
              </label>
              <select
                id="sprint-selector"
                className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                aria-label="Select sprint"
              >
                <option>Current Sprint</option>
              </select>
            </div>
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
          <ActiveComponent />
        </div>
      </main>
    </div>
  )
}
