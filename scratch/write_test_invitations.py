test_code = """import test from 'node:test';
import assert from 'node:assert/strict';
import {
  hashToken,
  generateInvitationToken,
  checkInviteRateLimit,
  resetInviteRateLimits,
  ALLOWED_ROLES,
} from '../base44/shared/invitations.js';

test('generateInvitationToken creates 64-char hex token', () => {
  const token = generateInvitationToken();
  assert.equal(typeof token, 'string');
  assert.equal(token.length, 64);
  assert.match(token, /^[0-9a-f]{64}$/);
});

test('hashToken produces consistent SHA-256 hash', async () => {
  const token = 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890';
  const hash1 = await hashToken(token);
  const hash2 = await hashToken(token);
  assert.equal(hash1, hash2);
  assert.equal(hash1.length, 64);

  // Different token has different hash
  const hashDifferent = await hashToken('different_token_123');
  assert.notEqual(hash1, hashDifferent);
});

test('checkInviteRateLimit limits invitations per business', () => {
  resetInviteRateLimits();
  const biz = 'biz_test_limit';

  for (let i = 0; i < 10; i++) {
    const res = checkInviteRateLimit(biz);
    assert.equal(res.allowed, true);
  }

  // 11th should be rate limited
  const blocked = checkInviteRateLimit(biz);
  assert.equal(blocked.allowed, false);
  assert.ok(blocked.waitMinutes > 0);

  resetInviteRateLimits();
});

test('ALLOWED_ROLES contains all 4 supported roles', () => {
  assert.deepEqual(ALLOWED_ROLES, ['admin', 'manager', 'tailor', 'user']);
});
"""

with open('/Users/ceooctapus/mehar/tests/invitations.test.js', 'w', encoding='utf-8') as f:
    f.write(test_code)
print('tests/invitations.test.js written')
