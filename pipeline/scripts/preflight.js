#!/usr/bin/env node
// Yooti pre-flight checks — runs on Mac, Linux, and Windows
// Usage: node pipeline/scripts/preflight.js

import { existsSync, readFileSync } from 'fs'
import { execSync } from 'child_process'

// ── Prerequisites — tools required before the pipeline can run ──

const config = existsSync('yooti.config.json')
  ? JSON.parse(readFileSync('yooti.config.json', 'utf8'))
  : {}

const prereqs = [
  {
    name:    'Git',
    command: 'git --version',
    install: {
      darwin:  'brew install git',
      win32:   'winget install Git.Git',
      linux:   'sudo apt-get install git',
    },
    required: true,
  },
  {
    name:    'GitHub CLI (gh)',
    command: 'gh --version',
    install: {
      darwin:  'brew install gh',
      win32:   'winget install GitHub.cli',
      linux:   'sudo apt-get install gh',
    },
    required: false,
    reason:   'Required for automatic PR creation in Phase 6',
  },
  {
    name:    'Node.js >= 20',
    command: 'node --version',
    versionCheck: v => parseInt(v.replace('v','').split('.')[0]) >= 20,
    install: {
      darwin:  'brew install node@20',
      win32:   'winget install OpenJS.NodeJS.LTS',
      linux:   'nvm install 20',
    },
    required: true,
  },
  {
    name:    'Python >= 3.12',
    command: process.platform === 'win32'
      ? 'python --version'
      : 'python3 --version 2>/dev/null || python --version',
    versionCheck: v => {
      const m = v.match(/(\d+)\.(\d+)/)
      return m && (parseInt(m[1]) > 3 || (parseInt(m[1]) === 3 && parseInt(m[2]) >= 12))
    },
    install: {
      darwin:  'brew install python@3.12',
      win32:   'winget install Python.Python.3.12',
      linux:   'sudo apt-get install python3.12',
    },
    required: config.stack?.includes('python') || config.projectType !== 'web',
  },
  {
    name:    'Docker Desktop',
    command: 'docker --version',
    install: {
      darwin:  'https://docs.docker.com/desktop/install/mac-install/',
      win32:   'https://docs.docker.com/desktop/install/windows-install/',
      linux:   'https://docs.docker.com/desktop/install/linux-install/',
    },
    required: config.deploy === 'docker',
    reason:   'Required for docker compose up',
  },
  {
    name:    'Docker Compose',
    command: 'docker compose version',
    install: {
      all: 'Included with Docker Desktop',
    },
    required: config.deploy === 'docker',
  },
]

console.log('\n◆ Checking prerequisites...\n')
let prereqFailed = false

for (const prereq of prereqs) {
  if (!prereq.required) continue
  try {
    const out = execSync(prereq.command, { encoding: 'utf8', stdio: 'pipe' }).trim()
    const versionOk = prereq.versionCheck ? prereq.versionCheck(out) : true
    if (versionOk) {
      console.log(`  \x1b[32m✓\x1b[0m ${prereq.name}`)
    } else {
      console.log(`  \x1b[31m✗\x1b[0m ${prereq.name} — version too old`)
      const platform = process.platform
      const cmd = prereq.install[platform] || prereq.install.all
      if (cmd) console.log(`    \x1b[2mInstall: ${cmd}\x1b[0m`)
      prereqFailed = true
    }
  } catch {
    console.log(`  \x1b[31m✗\x1b[0m ${prereq.name} — not found`)
    const platform = process.platform
    const cmd = prereq.install[platform] || prereq.install.all
    if (cmd) console.log(`    \x1b[2mInstall: ${cmd}\x1b[0m`)
    prereqFailed = true
  }
}

// Warn-only prereqs
for (const prereq of prereqs.filter(p => !p.required)) {
  try {
    execSync(prereq.command, { stdio: 'pipe' })
    console.log(`  \x1b[32m✓\x1b[0m ${prereq.name}`)
  } catch {
    console.log(`  \x1b[33m⚠\x1b[0m ${prereq.name} — not found (optional)`)
    if (prereq.reason) console.log(`    \x1b[2m${prereq.reason}\x1b[0m`)
    const platform = process.platform
    const cmd = prereq.install[platform] || prereq.install.all
    if (cmd) console.log(`    \x1b[2mInstall: ${cmd}\x1b[0m`)
  }
}

if (prereqFailed) {
  console.log('\n  \x1b[31m✗ Install missing prerequisites then run again.\x1b[0m\n')
  process.exit(1)
}

// ── Project checks ──

const results = []

function check(name, fn) {
  try {
    const result = fn()
    results.push({ name, pass: result !== false, reason: typeof result === 'string' ? result : null })
  } catch (err) {
    results.push({ name, pass: false, reason: err.message })
  }
}

// 1. Git repository exists
check('Git repository exists', () => {
  execSync('git rev-parse --git-dir', { stdio: 'ignore' })
  return true
})

// 2. Working tree is clean
check('Working tree is clean', () => {
  const out = execSync('git status --porcelain', { encoding: 'utf8' })
  const lines = out.split('\n').filter(Boolean)
  const trackedChanges = lines.filter(line => !line.startsWith('??'))
  if (trackedChanges.length > 0) {
    const files = trackedChanges.map(l => l.trim()).join(', ')
    throw new Error('Modified tracked files found: ' + files + '. Commit or stash before running.')
  }
  const untracked = lines.filter(line => line.startsWith('??'))
  if (untracked.length > 0) {
    return 'Pass — ' + untracked.length + ' untracked file(s) present (not blocking)'
  }
  return true
})

// 3. docker-compose.yml exists
check('docker-compose.yml exists', () => {
  if (!existsSync('docker-compose.yml')) throw new Error('docker-compose.yml not found in project root')
  return true
})

// 4. .claude/CLAUDE.md exists
check('.claude/CLAUDE.md exists', () => {
  if (!existsSync('.claude/CLAUDE.md')) throw new Error('.claude/CLAUDE.md not found — run yooti init')
  return true
})

// 5. yooti.config.json exists and is valid JSON
check('yooti.config.json is valid', () => {
  if (!existsSync('yooti.config.json')) throw new Error('yooti.config.json not found — run yooti init')
  try {
    JSON.parse(readFileSync('yooti.config.json', 'utf8'))
  } catch {
    throw new Error('yooti.config.json contains invalid JSON')
  }
  return true
})

// 6. Pipeline scripts exist
check('Pipeline scripts exist', () => {
  const required = [
    'pipeline/scripts/preflight.js',
    'pipeline/scripts/snapshot.py',
    'pipeline/scripts/regression-diff.py',
    'pipeline/scripts/generate-pr-body.py',
  ]
  const missing = required.filter(f => !existsSync(f))
  if (missing.length > 0) throw new Error('Missing: ' + missing.join(', '))
  return true
})

// 7. Example artifacts exist
check('Example artifacts exist', () => {
  if (!existsSync('.agent/examples')) throw new Error('.agent/examples not found — run yooti init')
  return true
})

// ── Results ──
const pass = results.filter(r => r.pass).length
const fail = results.filter(r => !r.pass).length

console.log('')
results.forEach(r => {
  if (r.pass) {
    const isWarn = typeof r.reason === 'string' && r.reason.includes('untracked')
    const icon = isWarn ? '\x1b[33m⚠\x1b[0m' : '\x1b[32m✓\x1b[0m'
    console.log('  ' + icon + ' ' + r.name)
    if (isWarn && r.reason) console.log('    \x1b[2m→ ' + r.reason + '\x1b[0m')
  } else {
    console.log('  \x1b[31m✗\x1b[0m ' + r.name)
    if (r.reason) console.log('    \x1b[2m→ ' + r.reason + '\x1b[0m')
  }
})

console.log('')
console.log('  ' + pass + '/' + results.length + ' checks passed')

if (fail > 0) {
  const s = fail > 1 ? 's' : ''
  console.log('\n  \x1b[31m' + fail + ' check' + s + ' failed. Fix the issues above before continuing.\x1b[0m\n')
  process.exit(1)
} else {
  console.log('  \x1b[32mAll checks passed. Ready to start sprint.\x1b[0m\n')
  process.exit(0)
}