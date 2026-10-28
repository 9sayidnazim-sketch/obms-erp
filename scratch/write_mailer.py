code = """// Shared Resend Email Client for THREDO (Base44 & Vercel)
// No external npm dependencies - uses standard fetch

export function maskEmail(email) {
  if (!email || typeof email !== 'string') return '***';
  const parts = email.trim().split('@');
  if (parts.length !== 2) return '***';
  const [local, domain] = parts;
  if (local.length <= 2) {
    return local[0] + '***@' + domain;
  }
  return local[0] + '***' + local[local.length - 1] + '@' + domain;
}

export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return re.test(email.trim());
}

export async function getSecret(key, passedSecrets = null) {
  if (passedSecrets && typeof passedSecrets.get === 'function') {
    try {
      const val = passedSecrets.get(key);
      if (val) return val;
    } catch (_) {}
  }
  try {
    if (typeof globalThis !== 'undefined' && globalThis.__B44_SECRETS__) {
      const val = globalThis.__B44_SECRETS__.get?.(key);
      if (val) return val;
    }
  } catch (_) {}
  try {
    const runtime = await import('base44:runtime');
    if (runtime?.secrets && typeof runtime.secrets.get === 'function') {
      const val = runtime.secrets.get(key);
      if (val) return val;
    }
  } catch (_) {}
  if (typeof process !== 'undefined' && process.env && process.env[key]) {
    return process.env[key];
  }
  return null;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Sends an email via Resend API
 * @param {Object} options
 * @param {string|string[]} options.to - Recipient email(s)
 * @param {string} options.subject - Email subject
 * @param {string} [options.html] - HTML body
 * @param {string} [options.text] - Plain text body
 * @param {string} [options.replyTo] - Reply-To header
 * @param {string} [options.from] - Custom from address (defaults to MAIL_FROM)
 * @param {Array<{filename: string, content: string}>} [options.attachments] - Base64 attachments
 * @param {string} [options.idempotencyKey] - Stable event idempotency key (max 256 chars)
 * @param {string} [options.templateName] - Optional template name for safe logging
 * @param {Object} [options.secrets] - Optional Base44 secrets object
 * @param {Function} [options.fetchFn] - Injectable fetch for unit tests
 * @returns {Promise<{ok: boolean, id?: string, status?: number, error?: string}>}
 */
export async function sendEmail({
  to,
  subject,
  html,
  text,
  replyTo,
  from,
  attachments,
  idempotencyKey,
  templateName = 'custom',
  secrets: passedSecrets = null,
  fetchFn = null,
}) {
  try {
    const fetchImpl = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
    if (!fetchImpl) {
      return { ok: false, error: 'fetch is not available in the current environment' };
    }

    // 1. Resolve configuration secrets
    const apiKey = await getSecret('RESEND_API_KEY', passedSecrets);
    if (!apiKey) {
      return { ok: false, error: 'RESEND_API_KEY is not configured' };
    }

    const defaultFrom = (await getSecret('MAIL_FROM', passedSecrets)) || 'THREDO <billing@mail.SENDING_DOMAIN>';
    const defaultReplyTo = await getSecret('MAIL_REPLY_TO', passedSecrets);
    const overrideTo = await getSecret('MAIL_OVERRIDE_TO', passedSecrets);

    // 2. Normalize and validate recipients
    let recipients = Array.isArray(to) ? to : [to];
    recipients = recipients
      .filter(Boolean)
      .map((r) => String(r).trim().toLowerCase())
      .filter((r) => r.length > 0);

    if (overrideTo && overrideTo.trim()) {
      recipients = [overrideTo.trim().toLowerCase()];
    }

    const validRecipients = recipients.filter(validateEmail);
    if (validRecipients.length === 0) {
      return { ok: false, error: 'No valid recipient email address provided' };
    }

    if (validRecipients.length > 50) {
      return { ok: false, error: 'Resend supports up to 50 recipients per email' };
    }

    if (!subject || typeof subject !== 'string' || !subject.trim()) {
      return { ok: false, error: 'Email subject is required' };
    }

    // 3. Prepare payload
    const payload = {
      from: from || defaultFrom,
      to: validRecipients,
      subject: subject.trim(),
    };

    if (html) payload.html = html;
    if (text) payload.text = text;
    if (!html && !text) {
      payload.text = '';
    }

    const effectiveReplyTo = replyTo || defaultReplyTo;
    if (effectiveReplyTo) {
      payload.reply_to = effectiveReplyTo;
    }

    if (Array.isArray(attachments) && attachments.length > 0) {
      payload.attachments = attachments.map((att) => ({
        filename: att.filename,
        content: att.content,
      }));
    }

    // 4. Headers with Idempotency
    const headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    };

    if (idempotencyKey && typeof idempotencyKey === 'string') {
      headers['Idempotency-Key'] = String(idempotencyKey).trim().slice(0, 256);
    }

    // 5. Send with exponential backoff on 429 and 5xx (max 3 attempts)
    const backoffDelays = [500, 1500, 3000];
    let lastError = null;
    let lastStatus = 500;

    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const res = await fetchImpl('https://api.resend.com/emails', {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });

        lastStatus = res.status;

        if (res.ok) {
          const json = await res.json().catch(() => ({}));
          const messageId = json?.id || 'resend_' + Date.now();

          const maskedRecipients = validRecipients.map(maskEmail).join(', ');
          console.log(`[Mailer] Sent message ${messageId} (template: ${templateName}) to ${maskedRecipients}`);

          return {
            ok: true,
            id: messageId,
            status: res.status,
          };
        }

        const errJson = await res.json().catch(() => ({}));
        const errMsg = errJson?.message || errJson?.error || `Resend API error (${res.status})`;

        // 429 Rate Limit or 5xx Server Error -> retry
        if (res.status === 429 || res.status >= 500) {
          lastError = errMsg;
          if (attempt < 2) {
            await sleep(backoffDelays[attempt]);
            continue;
          }
        } else {
          // Client errors (400, 401, 403, 422) fail immediately
          return {
            ok: false,
            status: res.status,
            error: errMsg,
          };
        }
      } catch (networkErr) {
        lastError = networkErr.message || 'Network error communicating with Resend';
        if (attempt < 2) {
          await sleep(backoffDelays[attempt]);
          continue;
        }
      }
    }

    return {
      ok: false,
      status: lastStatus,
      error: lastError || 'Failed to dispatch email after 3 attempts',
    };
  } catch (unexpectedErr) {
    return {
      ok: false,
      status: 500,
      error: unexpectedErr.message || 'Unexpected mailer error',
    };
  }
}
"""

with open('/Users/ceooctapus/mehar/base44/shared/mailer.js', 'w', encoding='utf-8') as f:
    f.write(code)
print('mailer.js written successfully')
