/**
 * API contract tests — yooti-dashboard
 * Verifies all endpoints respond with the correct shape.
 * Add one test per endpoint as API stories are completed.
 */
import { describe, it, expect } from 'vitest'
import request from 'supertest'
import { app } from '../../services/api/src/app'

describe('API contracts — health endpoints', () => {
  it('GET /health response matches contract', async () => {
    const res = await request(app).get('/health')
    expect(res.status).toBe(200)
    expect(res.body).toMatchObject({
      status: expect.stringMatching(/^(ok|degraded|down)$/),
    })
  })
})

// Add contract tests here as API stories complete
// Pattern:
//   describe('API contracts — [feature]', () => {
//     it('POST /api/v1/[endpoint] success response matches contract')
//     it('POST /api/v1/[endpoint] validation error matches contract')
//     it('POST /api/v1/[endpoint] auth error matches contract')
//   })
