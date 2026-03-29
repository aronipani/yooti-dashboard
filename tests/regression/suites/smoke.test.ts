/**
 * Smoke test suite — yooti-dashboard
 * Critical path tests. If any fail, the build is broken.
 * Target: complete in under 2 minutes.
 * Add one describe block per major feature as stories are completed.
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import request from 'supertest'
import { app } from '../../services/api/src/app'

describe('Smoke — API health', () => {
  it('GET /health returns 200', async () => {
    const res = await request(app).get('/health')
    expect(res.status).toBe(200)
  })

  it('GET /api/v1/status returns service info', async () => {
    const res = await request(app).get('/api/v1/status')
    expect(res.status).toBe(200)
    expect(res.body).toHaveProperty('version')
  })
})

describe('Smoke — Authentication', () => {
  it('protected endpoint returns 401 without token', async () => {
    const res = await request(app).get('/api/v1/protected')
    expect(res.status).toBe(401)
  })
})

// Add new describe blocks here as stories are completed
// Each block should test the critical path of one feature
// Keep total suite under 2 minutes
