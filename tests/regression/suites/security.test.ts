/**
 * Security regression tests — yooti-dashboard
 * Verifies security controls are not broken by new code.
 * These tests run on every PR — they must always pass.
 */
import { describe, it, expect } from 'vitest'
import request from 'supertest'
import { app } from '../../services/api/src/app'

describe('Security regression — authentication', () => {
  it('all protected routes return 401 without token', async () => {
    const protectedRoutes = [
      '/api/v1/users',
      '/api/v1/profile',
      // Add routes here as they are created
    ]
    for (const route of protectedRoutes) {
      const res = await request(app).get(route)
      expect(res.status, `${route} should require auth`).toBe(401)
    }
  })

  it('invalid JWT returns 401 not 500', async () => {
    const res = await request(app)
      .get('/api/v1/profile')
      .set('Authorization', 'Bearer invalid.jwt.token')
    expect(res.status).toBe(401)
    expect(res.status).not.toBe(500)
  })
})

describe('Security regression — input validation', () => {
  it('SQL injection attempt returns 400 not 500', async () => {
    const res = await request(app)
      .post('/api/v1/users/search')
      .send({ query: "\'; DROP TABLE users; --" })
    expect(res.status).toBe(400)
    expect(res.status).not.toBe(500)
  })
})

// Add security regression tests here as security stories complete