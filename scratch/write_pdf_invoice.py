code = """// Shared A4 PDF Invoice Generator for THREDO (Mehar Tailors)
// Generates official tax invoice adhering to AED currency formatting

import { jsPDF as defaultJsPDF } from 'jspdf';
import { companyName } from './company.js';

export function formatMoney(n, currency = 'AED') {
  return `${currency} ${Number(n || 0).toFixed(2)}`;
}

/**
 * Builds an official A4 tax invoice PDF
 * @param {Object} sale - Sale record or sale draft
 * @param {Object} [company] - Default company entity
 * @param {Function} [customJsPDF] - Optional jsPDF class injection for dual-runtime support
 * @returns {{ doc: any, arrayBuffer: ArrayBuffer, base64: string, fileName: string }}
 */
export function buildSaleBillPdf(sale, company, customJsPDF = null) {
  const PDFClass = customJsPDF || defaultJsPDF;
  const doc = new PDFClass({ unit: 'mm', format: 'a4' });
  const W = 210, H = 297, margin = 14, right = W - margin, bottom = H - 24;

  const currency = company?.currency || 'AED';
  const money = (n) => formatMoney(n, currency);

  // Header band
  doc.setFillColor(91, 61, 245);
  doc.rect(0, 0, W, 26, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(18);
  doc.text(companyName(company), margin, 12);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  const headParts = [
    company?.address,
    company?.phone,
    company?.email,
    company?.tax_number && `TRN: ${company.tax_number}`,
  ].filter(Boolean);
  doc.text(headParts.join('  •  ') || 'Retail Bill', margin, 18);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(15);
  doc.text('SALE INVOICE', right, 13, { align: 'right' });

  doc.setTextColor(33, 33, 40);
  let y = 36;

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(10);
  const invoiceId = sale.sale_id || sale.id || 'INV-0001';
  doc.text(`Invoice No: ${invoiceId}`, margin, y);
  doc.text(`Date: ${sale.date || new Date().toISOString().slice(0, 10)}`, right, y, { align: 'right' });
  y += 7;

  // Customer box
  doc.setFillColor(245, 245, 250);
  doc.roundedRect(margin, y - 4, W - margin * 2, 14, 2, 2, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.setTextColor(120, 120, 130);
  doc.text('CUSTOMER', margin + 4, y);
  doc.setTextColor(33, 33, 40);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.text(sale.customer_name || 'Walk-in Customer', margin + 4, y + 5);
  doc.setFontSize(9);
  doc.setTextColor(120, 120, 130);
  if (sale.customer_phone) doc.text(`Phone: ${sale.customer_phone}`, margin + 4, y + 9);
  if (sale.customer_email) doc.text(`Email: ${sale.customer_email}`, margin + 80, y + 9);
  y += 16;

  // Items table header
  doc.setTextColor(255, 255, 255);
  doc.setFillColor(91, 61, 245);
  doc.rect(margin, y - 4, W - margin * 2, 7, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text('#', margin + 2, y);
  doc.text('Item', margin + 14, y);
  doc.text('Qty', margin + 110, y);
  doc.text('Price', margin + 130, y);
  doc.text('Total', right - 2, y, { align: 'right' });
  doc.setTextColor(33, 33, 40);
  y += 5;

  // Items rows
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  const items = sale.items || [];
  items.forEach((it, i) => {
    if (y > bottom) {
      doc.addPage();
      y = 36;
    }
    if (i % 2 === 0) {
      doc.setFillColor(245, 245, 250);
      doc.rect(margin, y - 4, W - margin * 2, 6, 'F');
    }
    doc.setTextColor(33, 33, 40);
    doc.text(String(i + 1), margin + 2, y);
    doc.text(String(it.name || '—'), margin + 14, y);
    doc.text(String(it.quantity || 0), margin + 110, y);
    doc.text(money(it.price), margin + 130, y);
    doc.text(money(it.line_total), right - 2, y, { align: 'right' });
    y += 6;
  });

  // Totals
  y += 3;
  doc.setDrawColor(220, 220, 225);
  doc.line(margin, y, right, y);
  y += 6;
  const totalRows = [
    ['Subtotal', money(sale.subtotal)],
    ['Discount', `- ${money(sale.discount)}`],
    [`Tax (${sale.tax_percent || 0}%)`, money(sale.tax_amount)],
  ];
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(120, 120, 130);
  totalRows.forEach(([k, v]) => {
    doc.text(k, right - 60, y);
    doc.setTextColor(33, 33, 40);
    doc.text(v, right, y, { align: 'right' });
    y += 6;
  });
  doc.setDrawColor(220, 220, 225);
  doc.line(margin, y, right, y);
  y += 6;
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.setTextColor(33, 33, 40);
  doc.text('Total', margin, y);
  doc.text(money(sale.total), right, y, { align: 'right' });
  y += 7;
  doc.setFontSize(10);
  doc.setTextColor(16, 185, 129);
  doc.text('Amount Paid', margin, y);
  doc.text(money(sale.amount_paid), right, y, { align: 'right' });
  y += 6;
  doc.setTextColor(217, 119, 6);
  doc.text('Balance Due', margin, y);
  doc.text(money(sale.balance_due), right, y, { align: 'right' });

  // Footer
  doc.setDrawColor(220, 220, 225);
  doc.line(margin, H - 20, right, H - 20);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(120, 120, 130);
  doc.text(`Thank you for choosing ${companyName(company)}.`, margin, H - 14);
  doc.text('This is an official system-generated invoice.', margin, H - 10);
  doc.text(`Payment: ${sale.payment_method || '—'} (${sale.payment_status || '—'})`, right, H - 10, {
    align: 'right',
  });

  const arrayBuffer = doc.output('arraybuffer');
  let base64 = '';
  try {
    if (typeof Buffer !== 'undefined') {
      base64 = Buffer.from(arrayBuffer).toString('base64');
    } else {
      const bytes = new Uint8Array(arrayBuffer);
      let binary = '';
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      base64 = btoa(binary);
    }
  } catch (_) {}

  const fileName = `${invoiceId}.pdf`;

  return {
    doc,
    arrayBuffer,
    base64,
    fileName,
  };
}
"""

with open('/Users/ceooctapus/mehar/base44/shared/pdfInvoice.js', 'w', encoding='utf-8') as f:
    f.write(code)
print('pdfInvoice.js written successfully')
