# React Constitution — yooti-dashboard

## Purpose
Defines how React components and frontend code are written.
Agent reads this before writing any React, TSX, or CSS file.

---

## Component rules

Every component is a function — no class components:
  export function UserCard({ user }: UserCardProps)          ✓
  export class UserCard extends React.Component              ✗

One component per file. File name matches component name:
  UserCard.tsx exports UserCard                              ✓
  Multiple components in one file                            ✗

Props interface defined above the component, not inline:
  interface UserCardProps {
    user: User
    onSelect?: (userId: string) => void
  }
  export function UserCard({ user, onSelect }: UserCardProps)

Default export only for pages. Named exports for everything else:
  // components/UserCard.tsx
  export function UserCard(...)                              ✓ named
  // pages/UserProfile.tsx
  export default function UserProfilePage(...)               ✓ default

---

## Component structure — follow this order

1. Props interface
2. Component function declaration
3. Hooks (useState, useEffect, custom hooks) — at the top
4. Derived state and computed values
5. Event handlers (prefixed with handle)
6. Early returns (loading, error states)
7. Main render return

---

## Hooks rules

Custom hooks — always prefixed with use:
  function useUserProfile(userId: string)                    ✓
  function getUserProfile(userId: string)                    ✗

No business logic in components — extract to custom hooks:
  // in UserCard.tsx                                         ✗
  const [user, setUser] = useState(null)
  useEffect(() => { fetch('/api/users/' + id).then(...) }, [id])

  // in useUser.ts                                           ✓
  export function useUser(id: string) { ... }

useEffect dependencies — always complete, never lie:
  useEffect(() => { fetchUser(userId) }, [userId])           ✓
  useEffect(() => { fetchUser(userId) }, [])                 ✗ missing dep

No useEffect for derived state — use useMemo:
  const fullName = useMemo(
    () => \`\${user.firstName} \${user.lastName}\`,
    [user.firstName, user.lastName]
  )

---

## Styling — Tailwind CSS

Use Tailwind utility classes — no inline styles:
  <div style={{ color: 'red' }}>                             ✗
  <div className="text-red-500">                             ✓

Use shadcn/ui components — do not rebuild primitives:
  <button className="...">Submit</button>                    ✗ if Button exists
  <Button variant="default">Submit</Button>                  ✓

Responsive — mobile first, always:
  className="text-sm md:text-base lg:text-lg"                ✓
  No fixed widths in pixels — use Tailwind sizing

Conditional classes — use clsx or cn():
  className={\`btn \${isActive ? 'btn-active' : ''}\`}         ✗
  className={cn('btn', isActive && 'btn-active')}             ✓

---

## Accessibility — mandatory, not optional

Every interactive element must be keyboard accessible.
Every image must have meaningful alt text:
  <img src="..." />                                          ✗
  <img src="..." alt="User profile photo for Sarah Chen" />  ✓
  <img src="decorative.png" alt="" role="presentation" />    ✓ for decorative

Form inputs must have associated labels:
  <input type="email" />                                     ✗
  <label htmlFor="email">Email</label>
  <input id="email" type="email" />                          ✓

ARIA labels for icon-only buttons:
  <button><CloseIcon /></button>                             ✗
  <button aria-label="Close dialog"><CloseIcon /></button>   ✓

Colour contrast — WCAG AA minimum (4.5:1 for text).
Run axe-core in every component test — 0 violations required.

---

## State management

Local state — useState for component-local UI state only.
Server state — React Query (TanStack Query) for all API data.
Global UI state — React Context for theme, auth, locale only.
Never store server data in Context — that is what React Query is for.

React Query patterns:
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => userApi.getById(userId),
  })

Always handle loading and error states explicitly:
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  // then render data

---

## Testing — Vitest + Testing Library + axe-core

Every component has a test file: UserCard.test.tsx
Test the behaviour, not the implementation:
  expect(screen.getByRole('button', { name: 'Submit' }))     ✓
  expect(wrapper.find('.submit-btn'))                         ✗

Accessibility test in every component test:
  import { axe } from 'jest-axe'
  it('has no accessibility violations', async () => {
    const { container } = render(<UserCard user={mockUser} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

---

## What is banned

dangerouslySetInnerHTML — without explicit security review
Direct DOM manipulation — use refs only when necessary
Index as key in lists — use stable unique IDs
  items.map((item, index) => <Item key={index} />)           ✗
  items.map(item => <Item key={item.id} />)                  ✓
Nested ternaries in JSX — extract to variables
Any component over 200 lines — split it

## Self-audit — mandatory before marking any React task COMPLETE

Run this checklist before marking COMPLETE.
Write results to .agent/evidence/{STORY-ID}/code-audit.md.

  SECURITY
  ☐ No API keys or secrets in any component or hook
  ☐ All API calls go through api-client.ts — no fetch() directly
  ☐ No dangerouslySetInnerHTML without sanitisation
  ☐ No sensitive data in localStorage or sessionStorage

  CODE QUALITY
  ☐ Every component has TypeScript props interface defined
  ☐ No any type used anywhere
  ☐ No useEffect with missing dependencies
  ☐ No console.log debug statements
  ☐ No inline styles — Tailwind classes only
  ☐ Every component handles loading state
  ☐ Every component handles error state
  ☐ No TODO or FIXME in production code

  ACCESSIBILITY
  ☐ axe-core test in every component test file
  ☐ axe-core asserts 0 violations
  ☐ All images have alt text
  ☐ All form inputs have associated labels
  ☐ Interactive elements are keyboard navigable

  TESTS
  ☐ Test file exists for every new component
  ☐ Loading state tested
  ☐ Error state tested
  ☐ No real API calls in tests — MSW or vi.mock used

  SCANNING
  ☐ eslint: 0 errors, 0 warnings
  ☐ tsc --noEmit: 0 errors
  ☐ vitest: 100% passing
  ☐ axe-core: 0 violations in all component tests
