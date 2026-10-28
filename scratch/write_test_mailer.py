test_code = """import test from 'node:test';
import assert from 'node:assert/strict';
import { sendEmail, maskEmail, validateEmail } from '../base44/shared/mailer.js';

test('maskEmail correctly masks local parts', () => {
  assert.equal(maskEmail('a@domain.com'), 'a***@domain.com');
  assert.equal(maskEmail('ab@domain.com'), 'a***@domain.com');
  assert.equal(maskEmail('john.doe@example.com'), 'j***e@example.com');
  assert.equal(maskEmail('invalid'), '***');
  assert.equal(maskEmail(null), '***');
});

test('validateEmail validates format', () => {
  assert.equal(validateEmail('test@example.com'), true);
  assert.equal(validateEmail('user.name+tag@sub.domain.co'), true);
  assert.equal(validateEmail('invalid'), false);
  assert.equal(validateEmail('@domain.com'), false);
  assert.equal(validateEmail('test@'), false);
});

test('sendEmail fails if RESEND_API_KEY is missing', async () => {
  const origKey = process.env.RESEND_API_KEY;
  delete process.env.RESEND_API_KEY;

  const result = await sendEmail({
    to: 'customer@example.com',
    subject: 'Test Subject',
    text: 'Hello',
    fetchFn: async () => assert.fail('fetch should not be called'),
  });

  assert.equal(result.ok, false);
  assert.match(result.error, /RESEND_API_KEY is not configured/);

  if (origKey) process.env.RESEND_API_KEY = origKey;
});

test('sendEmail fails on invalid recipients', async () => {
  process.env.RESEND_API_KEY = 're_test_key_123';

  const result = await sendEmail({
    to: ['not-an-email', 'also-bad'],
    subject: 'Test Subject',
    text: 'Hello',
    fetchFn: async () => assert.fail('fetch should not be called'),
  });

  assert.equal(result.ok, false);
  assert.match(result.error, /No valid recipient/);
});

test('sendEmail succeeds and passes Idempotency-Key header', async () => {
  process.env.RESEND_API_KEY = 're_test_key_123';
  let capturedHeaders = null;
  let capturedBody = null;

  const mockFetch = async (url, options) => {
    assert.equal(url, 'https://api.resend.com/emails');
    capturedHeaders = options.headers;
    capturedBody = JSON.parse(options.body);

    return {
      ok: true,
      status: 200,
      json: async () => ({ id: 'email_msg_98765' }),
    };
  };

  const result = await sendEmail({
    to: 'customer@example.com',
    subject: 'Invoice Attached',
    html: '<p>Invoice</p>',
    idempotencyKey: 'invoice:INV-001:1',
    templateName: 'invoice',
    fetchFn: mockFetch,
  });

  assert.equal(result.ok, true);
  assert.equal(result.id, 'email_msg_98765');
  assert.equal(capturedHeaders['Authorization'], 'Bearer re_test_key_123');
  assert.equal(capturedHeaders['Idempotency-Key'], 'invoice:INV-001:1');
  assert.deepEqual(capturedBody.to, ['customer@example.com']);
  assert.equal(capturedBody.subject, 'Invoice Attached');
  assert.equal(capturedBody.html, '<p>Invoice</p>');
});

test('sendEmail retries on 429 and succeeds', async () => {
  process.env.RESEND_API_KEY = 're_test_key_123';
  let attempts = 0;

  const mockFetch = async () => {
    attempts++;
    if (attempts === 1) {
      return {
        ok: false,
        status: 429,
        json: async () => ({ message: 'Rate limit exceeded' }),
      };
    }
    return {
      ok: true,
      status: 200,
      json: async () => ({ id: 'email_after_retry' }),
    };
  };

  const result = await sendEmail({
    to: 'retry@example.com',
    subject: 'Retry Test',
    text: 'Retrying',
    fetchFn: mockFetch,
  });

  assert.equal(result.ok, true);
  assert.equal(result.id, 'email_after_retry');
  assert.equal(attempts, 2);
});

test('sendEmail does NOT retry on 400 Bad Request', async () => {
  process.env.RESEND_API_KEY = 're_test_key_123';
  let attempts = 0;

  const mockFetch = async () => {
    attempts++;
    return {
      ok: false,
      status: 400,
      json: async () => ({ message: 'Validation failed' }),
    };
  };

  const result = await sendEmail({
    to: 'clienterror@example.com',
    subject: 'Bad Request',
    text: 'Bad',
    fetchFn: mockFetch,
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, 400);
  assert.equal(attempts, 1);
});

test('sendEmail honors MAIL_OVERRIDE_TO in non-prod', async () => {
  process.env.RESEND_API_KEY = 're_test_key_123';
  process.env.MAIL_OVERRIDE_TO = 'safe-dev@example.com';
  let capturedBody = null;

  const mockFetch = async (url, options) => {
    capturedBody = JSON.parse(options.body);
    return {
      ok: true,
      status: 200,
      json: async () => ({ id: 'override_msg_1' }),
    };
  };

  const result = await sendEmail({
    to: 'real-customer@live.com',
    subject: 'Confidential Invoice',
    text: 'Bill',
    fetchFn: mockFetch,
  });

  assert.equal(result.ok, true);
  assert.deepEqual(capturedBody.to, ['safe-dev@example.com']);

  delete process.env.MAIL_OVERRIDE_TO;
});
"""

with open('/Users/ceooctapus/mehar/tests/mailer.test.js', 'w', encoding='utf-8') as f:
    f.write(test_code)
print('tests/mailer.test.js written')
