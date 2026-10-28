test_code = """import test from 'node:test';
import assert from 'node:assert/strict';
import {
  escapeHtml,
  renderEmailLayout,
  invoiceEmail,
  onlineOrderReceivedEmail,
  paymentReferenceReceivedEmail,
  paymentApprovedEmail,
  paymentRejectedEmail,
  accessRevokedEmail,
  subscriptionReminderEmail,
  couponPassActivatedEmail,
  staffInvitationEmail,
} from '../base44/shared/emailTemplates.js';

const EMOJI_REGEX = /[\\p{Extended_Pictographic}\\p{Regional_Indicator}\\uFE0F]/u;

test('escapeHtml prevents XSS injections', () => {
  const dirty = '<script>alert("xss")</script> & "foo" \\'bar\\'';
  const clean = escapeHtml(dirty);
  assert.equal(clean.includes('<script>'), false);
  assert.equal(clean.includes('&lt;script&gt;'), true);
  assert.equal(clean.includes('&amp;'), true);
  assert.equal(clean.includes('&quot;'), true);
  assert.equal(clean.includes('&#039;'), true);
});

test('all 9 email templates render correctly with zero emojis', () => {
  const dummyCompany = { name: 'Mehar Tailors LLC', currency: 'AED' };

  const templates = [
    invoiceEmail({
      sale: { sale_id: 'INV-100', total: 500, amount_paid: 500, balance_due: 0, date: '2026-10-26' },
      company: dummyCompany,
    }),
    onlineOrderReceivedEmail({
      orderId: 'ORD-100',
      orderType: 'tailoring',
      customerName: 'Fatima Al Zarooni',
      total: 350,
      company: dummyCompany,
    }),
    paymentReferenceReceivedEmail({
      submissionId: 'sub_1',
      referenceNumber: 'REF-PAY-99',
      businessName: 'Al Nuaimi Tailoring',
      company: dummyCompany,
    }),
    paymentApprovedEmail({
      businessName: 'Al Nuaimi Tailoring',
      planName: 'Yearly Pro',
      expiresAt: '2027-10-26T00:00:00.000Z',
      company: dummyCompany,
    }),
    paymentRejectedEmail({
      businessName: 'Al Nuaimi Tailoring',
      referenceNumber: 'REF-BAD-01',
      reason: 'Transaction not found in bank statement',
      company: dummyCompany,
    }),
    accessRevokedEmail({
      businessName: 'Al Nuaimi Tailoring',
      reason: 'Policy non-compliance',
      company: dummyCompany,
    }),
    subscriptionReminderEmail({
      businessName: 'Al Nuaimi Tailoring',
      hoursRemaining: 24,
      expiresAt: '2026-10-27T00:00:00.000Z',
      company: dummyCompany,
    }),
    couponPassActivatedEmail({
      code: 'FREE48',
      durationHours: 48,
      expiresAt: '2026-10-28 12:00 PM',
      company: dummyCompany,
    }),
    staffInvitationEmail({
      role: 'manager',
      acceptUrl: 'https://thredo.com/invite/accept?token=xyz123',
      businessName: 'Mehar Tailors',
      company: dummyCompany,
    }),
  ];

  for (const t of templates) {
    assert.ok(t.subject);
    assert.ok(t.preheader);
    assert.ok(t.html);
    assert.ok(t.text);

    // Assert zero emojis in all fields
    assert.equal(EMOJI_REGEX.test(t.subject), false, `Emoji found in subject: ${t.subject}`);
    assert.equal(EMOJI_REGEX.test(t.preheader), false, `Emoji found in preheader: ${t.preheader}`);
    assert.equal(EMOJI_REGEX.test(t.html), false, `Emoji found in html of ${t.subject}`);
    assert.equal(EMOJI_REGEX.test(t.text), false, `Emoji found in text of ${t.subject}`);
  }
});
"""

with open('/Users/ceooctapus/mehar/tests/emailTemplates.test.js', 'w', encoding='utf-8') as f:
    f.write(test_code)
print('tests/emailTemplates.test.js written')
