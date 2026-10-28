test_code = """import test from 'node:test';
import assert from 'node:assert/strict';
import { buildSaleBillPdf, formatMoney } from '../base44/shared/pdfInvoice.js';

test('formatMoney formats amounts with currency prefix', () => {
  assert.equal(formatMoney(100), 'AED 100.00');
  assert.equal(formatMoney(0), 'AED 0.00');
  assert.equal(formatMoney(12.5, 'AED'), 'AED 12.50');
  assert.equal(formatMoney('55.99'), 'AED 55.99');
});

test('buildSaleBillPdf generates valid PDF buffer and base64', () => {
  const sale = {
    sale_id: 'INV-TEST-001',
    customer_name: 'Ahmed Al Mansoori',
    customer_phone: '+971501112233',
    customer_email: 'ahmed@example.com',
    date: '2026-10-26',
    items: [
      { name: 'Custom Kandora', quantity: 2, price: 250, line_total: 500 },
      { name: 'Buttons & Stitching', quantity: 1, price: 50, line_total: 50 },
    ],
    subtotal: 550,
    discount: 50,
    tax_percent: 5,
    tax_amount: 25,
    total: 525,
    amount_paid: 525,
    balance_due: 0,
    payment_method: 'Card',
    payment_status: 'Paid',
  };

  const company = {
    name: 'Mehar Tailors LLC',
    address: 'Meena Bazaar, Dubai',
    phone: '+971 4 123 4567',
    tax_number: '100200300400003',
    currency: 'AED',
  };

  const result = buildSaleBillPdf(sale, company);

  assert.ok(result.doc);
  assert.ok(result.arrayBuffer);
  assert.ok(result.arrayBuffer.byteLength > 1000);
  assert.ok(typeof result.base64 === 'string');
  assert.ok(result.base64.length > 500);
  assert.equal(result.fileName, 'INV-TEST-001.pdf');
});
"""

with open('/Users/ceooctapus/mehar/tests/pdfInvoice.test.js', 'w', encoding='utf-8') as f:
    f.write(test_code)
print('tests/pdfInvoice.test.js written')
