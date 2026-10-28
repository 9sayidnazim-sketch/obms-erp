code = """// Shared Email Layout & Event Templates for THREDO (Mehar Tailors)
// Enforces zero emojis, strict HTML escaping, and responsive typography

import { companyName } from './company.js';
import { formatMoney } from './pdfInvoice.js';

export function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Shared Responsive HTML Layout Shell (Zero Emojis)
 */
export function renderEmailLayout({ title, preheader, contentHtml, footerNote, company }) {
  const brand = escapeHtml(companyName(company));
  const cleanTitle = escapeHtml(title || brand);
  const cleanPreheader = escapeHtml(preheader || '');
  const cleanFooterNote = footerNote ? `<p style="margin: 8px 0 0; font-size: 11px; color: #888888;">${escapeHtml(footerNote)}</p>` : '';

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${cleanTitle}</title>
  <!--[if mso]>
  <style type="text/css">
    table, td, p, a { font-family: Arial, sans-serif !important; }
  </style>
  <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #F4F4F6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; color: #1A1A1A;">
  <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; line-height: 1px; color: #F4F4F6;">
    ${cleanPreheader}
  </div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #F4F4F6; width: 100%; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 580px; width: 100%; background-color: #FFFFFF; border: 1px solid #E2E2E6; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
          <!-- Brand Header -->
          <tr>
            <td style="background-color: #1A1A1A; padding: 24px 32px; text-align: left;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <span style="font-size: 18px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.02em; display: inline-block;">${brand}</span>
                  </td>
                  <td align="right" style="font-size: 12px; color: #A0A0A0; font-weight: 500;">
                    THREDO POS
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td style="padding: 32px; font-size: 14px; line-height: 1.6; color: #2A2A2A;">
              ${contentHtml}
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #FAFAFB; border-top: 1px solid #ECECEE; padding: 20px 32px; font-size: 12px; line-height: 1.5; color: #6E6E73; text-align: center;">
              <p style="margin: 0; font-weight: 500;">${brand} &bull; Tailoring &amp; Retail POS</p>
              <p style="margin: 4px 0 0; color: #8E8E93; font-size: 11px;">This is an automated system notification. Please do not reply directly to this email.</p>
              ${cleanFooterNote}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;
}

// 1. Invoice Email
export function invoiceEmail({ sale, company }) {
  const brand = companyName(company);
  const invId = sale.sale_id || sale.id || 'INV-0001';
  const currency = company?.currency || 'AED';
  const totalStr = formatMoney(sale.total, currency);
  const paidStr = formatMoney(sale.amount_paid, currency);
  const balanceStr = formatMoney(sale.balance_due, currency);
  const dateStr = sale.date || new Date().toISOString().slice(0, 10);
  const customerName = sale.customer_name || 'Valued Customer';

  const subject = `Tax Invoice ${invId} from ${brand}`;
  const preheader = `Your official tax invoice for ${totalStr} is attached.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #111111;">Tax Invoice</h2>
      <p style="margin: 0 0 16px;">Dear ${escapeHtml(customerName)},</p>
      <p style="margin: 0 0 20px; color: #444444;">Thank you for your business. Your official tax invoice <strong>${escapeHtml(invId)}</strong> has been generated and is attached to this email as a PDF document.</p>
      
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #F8F8FA; border: 1px solid #EAEAEA; border-radius: 8px; margin: 0 0 24px; padding: 16px;">
        <tr>
          <td style="padding: 6px 0; font-size: 13px; color: #666666;">Invoice Number:</td>
          <td align="right" style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #111111;">${escapeHtml(invId)}</td>
        </tr>
        <tr>
          <td style="padding: 6px 0; font-size: 13px; color: #666666;">Issue Date:</td>
          <td align="right" style="padding: 6px 0; font-size: 13px; color: #111111;">${escapeHtml(dateStr)}</td>
        </tr>
        <tr>
          <td style="padding: 6px 0; font-size: 13px; color: #666666;">Payment Method:</td>
          <td align="right" style="padding: 6px 0; font-size: 13px; color: #111111;">${escapeHtml(sale.payment_method || 'Standard')}</td>
        </tr>
        <tr style="border-top: 1px solid #E0E0E0;">
          <td style="padding: 10px 0 6px; font-size: 14px; font-weight: 700; color: #111111;">Total Amount:</td>
          <td align="right" style="padding: 10px 0 6px; font-size: 15px; font-weight: 700; color: #111111;">${escapeHtml(totalStr)}</td>
        </tr>
        <tr>
          <td style="padding: 4px 0; font-size: 13px; color: #10B981; font-weight: 600;">Amount Paid:</td>
          <td align="right" style="padding: 4px 0; font-size: 13px; color: #10B981; font-weight: 600;">${escapeHtml(paidStr)}</td>
        </tr>
        ${Number(sale.balance_due) > 0 ? `
        <tr>
          <td style="padding: 4px 0; font-size: 13px; color: #D97706; font-weight: 600;">Balance Due:</td>
          <td align="right" style="padding: 4px 0; font-size: 13px; color: #D97706; font-weight: 600;">${escapeHtml(balanceStr)}</td>
        </tr>` : ''}
      </table>

      <p style="margin: 0; font-size: 13px; color: #666666;">Please find your printable PDF tax invoice attached for your tax and accounting records.</p>
    `,
  });

  const text = `TAX INVOICE - ${brand}
Invoice No: ${invId}
Date: ${dateStr}
Customer: ${customerName}

Total Amount: ${totalStr}
Amount Paid: ${paidStr}
${Number(sale.balance_due) > 0 ? `Balance Due: ${balanceStr}\n` : ''}Payment Method: ${sale.payment_method || 'Standard'}

Your official tax invoice PDF is attached to this email.
Thank you for choosing ${brand}.`;

  return { subject, preheader, html, text };
}

// 2. Online Order Received Email
export function onlineOrderReceivedEmail({ orderId, orderType, customerName, items, total, company }) {
  const brand = companyName(company);
  const currency = company?.currency || 'AED';
  const totalStr = total ? formatMoney(total, currency) : null;
  const subject = `Order Confirmation ${orderId} - ${brand}`;
  const preheader = `We received your online ${orderType || 'tailoring'} order.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #111111;">Order Confirmed</h2>
      <p style="margin: 0 0 16px;">Dear ${escapeHtml(customerName || 'Customer')},</p>
      <p style="margin: 0 0 20px; color: #444444;">We have successfully received your order <strong>${escapeHtml(orderId)}</strong>. Our workshop team is reviewing your requirements.</p>

      <div style="background-color: #F8F8FA; border: 1px solid #EAEAEA; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 8px; font-size: 13px; color: #666666;"><strong>Order Reference:</strong> ${escapeHtml(orderId)}</p>
        <p style="margin: 0 0 8px; font-size: 13px; color: #666666;"><strong>Order Type:</strong> ${escapeHtml(orderType || 'Tailoring')}</p>
        ${totalStr ? `<p style="margin: 0; font-size: 14px; font-weight: 700; color: #111111;">Total: ${escapeHtml(totalStr)}</p>` : ''}
      </div>

      <p style="margin: 0; font-size: 13px; color: #666666;">We will notify you as soon as your garments enter cutting and stitching.</p>
    `,
  });

  const text = `ORDER CONFIRMATION - ${brand}
Order Reference: ${orderId}
Order Type: ${orderType || 'Tailoring'}
${totalStr ? `Total: ${totalStr}\n` : ''}
Dear ${customerName || 'Customer'},
We received your order and are currently processing it. Thank you for choosing ${brand}.`;

  return { subject, preheader, html, text };
}

// 3. Payment Reference Received Email
export function paymentReferenceReceivedEmail({ submissionId, referenceNumber, businessName, company }) {
  const brand = companyName(company);
  const subject = `Payment Reference Received - ${referenceNumber}`;
  const preheader = `A new payment reference ${referenceNumber} has been submitted.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #111111;">Payment Reference Submitted</h2>
      <p style="margin: 0 0 16px; color: #444444;">A PayNow reference has been submitted and is currently pending verification.</p>
      
      <div style="background-color: #F8F8FA; border: 1px solid #EAEAEA; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 8px; font-size: 13px; color: #666666;"><strong>Business:</strong> ${escapeHtml(businessName || 'Tenant Business')}</p>
        <p style="margin: 0 0 8px; font-size: 13px; color: #666666;"><strong>Reference:</strong> ${escapeHtml(referenceNumber)}</p>
        <p style="margin: 0; font-size: 13px; color: #666666;"><strong>Status:</strong> 48-Hour Provisional Access Active</p>
      </div>

      <p style="margin: 0; font-size: 13px; color: #666666;">The verification team will review bank records within 24 to 48 hours.</p>
    `,
  });

  const text = `PAYMENT REFERENCE SUBMITTED - ${brand}
Business: ${businessName || 'Tenant Business'}
Reference: ${referenceNumber}
Status: 48-Hour Provisional Access Active

Your payment submission is queued for administrative verification.`;

  return { subject, preheader, html, text };
}

// 4. Payment Approved Email
export function paymentApprovedEmail({ businessName, planName, expiresAt, company }) {
  const brand = companyName(company);
  const subject = `Payment Verified - Subscription Active`;
  const preheader = `Your payment was verified. Subscription active until ${expiresAt.slice(0, 10)}.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #10B981;">Payment Approved</h2>
      <p style="margin: 0 0 16px; color: #444444;">We are pleased to inform you that your payment reference has been verified and approved.</p>

      <div style="background-color: #F0FDF4; border: 1px solid #DCFCE7; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 8px; font-size: 13px; color: #166534;"><strong>Business:</strong> ${escapeHtml(businessName || 'Business Account')}</p>
        <p style="margin: 0 0 8px; font-size: 13px; color: #166534;"><strong>Plan:</strong> ${escapeHtml(planName || 'Active Commercial Plan')}</p>
        <p style="margin: 0; font-size: 13px; color: #166534;"><strong>Valid Until:</strong> ${escapeHtml(expiresAt.slice(0, 10))}</p>
      </div>

      <p style="margin: 0; font-size: 13px; color: #666666;">Your single-link tailoring access and cloud services are fully active.</p>
    `,
  });

  const text = `PAYMENT APPROVED - ${brand}
Business: ${businessName || 'Business Account'}
Plan: ${planName || 'Active Commercial Plan'}
Valid Until: ${expiresAt.slice(0, 10)}

Your payment was verified and your subscription has been extended.`;

  return { subject, preheader, html, text };
}

// 5. Payment Rejected Email
export function paymentRejectedEmail({ businessName, referenceNumber, reason, company }) {
  const brand = companyName(company);
  const subject = `Payment Verification Update - Action Required`;
  const preheader = `Payment reference ${referenceNumber} could not be verified.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #DC2626;">Payment Verification Notice</h2>
      <p style="margin: 0 0 16px; color: #444444;">Your submitted payment reference <strong>${escapeHtml(referenceNumber)}</strong> could not be verified.</p>

      <div style="background-color: #FEF2F2; border: 1px solid #FEE2E2; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 6px; font-size: 13px; font-weight: 700; color: #991B1B;">Reason for Rejection:</p>
        <p style="margin: 0; font-size: 13px; color: #991B1B;">${escapeHtml(reason || 'Unable to reconcile payment reference with bank records.')}</p>
      </div>

      <p style="margin: 0 0 16px; font-size: 13px; color: #444444;">Please sign in to your dashboard at your earliest convenience to submit a valid payment reference or contact support.</p>
    `,
  });

  const text = `PAYMENT REJECTED - ${brand}
Reference: ${referenceNumber}
Reason: ${reason || 'Unable to reconcile payment reference with bank records.'}

Please sign in to your dashboard to submit a valid reference or contact support.`;

  return { subject, preheader, html, text };
}

// 6. Access Revoked Email
export function accessRevokedEmail({ businessName, reason, company }) {
  const brand = companyName(company);
  const subject = `Account Access Status Update`;
  const preheader = `Account access has been suspended or revoked.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #111111;">Access Update</h2>
      <p style="margin: 0 0 16px; color: #444444;">Access for <strong>${escapeHtml(businessName || 'Business')}</strong> has been revoked by system administrators.</p>

      ${reason ? `
      <div style="background-color: #F8F8FA; border: 1px solid #EAEAEA; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 6px; font-size: 13px; font-weight: 600; color: #444444;">Details:</p>
        <p style="margin: 0; font-size: 13px; color: #666666;">${escapeHtml(reason)}</p>
      </div>` : ''}

      <p style="margin: 0; font-size: 13px; color: #666666;">If you believe this is in error, please reach out to your administrator or technical support.</p>
    `,
  });

  const text = `ACCESS REVOKED - ${brand}
Business: ${businessName || 'Business'}
${reason ? `Reason: ${reason}\n` : ''}
Please contact system support for assistance.`;

  return { subject, preheader, html, text };
}

// 7. Subscription Reminder Email
export function subscriptionReminderEmail({ businessName, hoursRemaining, expiresAt, company }) {
  const brand = companyName(company);
  const is24h = hoursRemaining <= 24;
  const subject = is24h ? `Subscription Renewal - Expiring in 24 Hours` : `Subscription Renewal Reminder - 3 Days Remaining`;
  const preheader = `Your subscription will expire on ${expiresAt.slice(0, 10)}. Renew now to prevent service interruption.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #D97706;">Subscription Expiring Soon</h2>
      <p style="margin: 0 0 16px; color: #444444;">This is a courtesy reminder that your subscription for <strong>${escapeHtml(businessName || 'Business Account')}</strong> will expire on <strong>${escapeHtml(expiresAt.slice(0, 10))}</strong>.</p>

      <div style="background-color: #FFFBEB; border: 1px solid #FEF3C7; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0; font-size: 13px; color: #92400E; font-weight: 600;">Time Remaining: Less than ${hoursRemaining} hours</p>
      </div>

      <p style="margin: 0; font-size: 13px; color: #666666;">Please renew your plan from the dashboard to ensure continuous tailoring and sales operations.</p>
    `,
  });

  const text = `SUBSCRIPTION RENEWAL REMINDER - ${brand}
Business: ${businessName || 'Business Account'}
Expiration Date: ${expiresAt.slice(0, 10)}
Time Remaining: Less than ${hoursRemaining} hours

Please renew your subscription to maintain uninterrupted service.`;

  return { subject, preheader, html, text };
}

// 8. Coupon Pass Activated Email
export function couponPassActivatedEmail({ code, durationHours, expiresAt, company }) {
  const brand = companyName(company);
  const subject = `Promotional Access Pass Activated`;
  const preheader = `Your ${durationHours}-hour access pass (${code}) is active.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #10B981;">Pass Activated</h2>
      <p style="margin: 0 0 16px; color: #444444;">Your promotional access pass <strong>${escapeHtml(code)}</strong> has been activated successfully.</p>

      <div style="background-color: #F0FDF4; border: 1px solid #DCFCE7; border-radius: 8px; padding: 16px; margin: 0 0 24px;">
        <p style="margin: 0 0 8px; font-size: 13px; color: #166534;"><strong>Duration:</strong> ${durationHours} Hours</p>
        <p style="margin: 0; font-size: 13px; color: #166534;"><strong>Active Until:</strong> ${escapeHtml(expiresAt)}</p>
      </div>

      <p style="margin: 0; font-size: 13px; color: #666666;">You now have full access to tailoring operations, inventory, and POS features.</p>
    `,
  });

  const text = `PROMOTIONAL PASS ACTIVATED - ${brand}
Code: ${code}
Duration: ${durationHours} Hours
Active Until: ${expiresAt}

You now have full access to THREDO features.`;

  return { subject, preheader, html, text };
}

// 9. Staff Invitation Email
export function staffInvitationEmail({ role, acceptUrl, businessName, company }) {
  const brand = companyName(company);
  const subject = `Invitation to join ${brand} on THREDO`;
  const preheader = `You have been invited to join ${brand} as ${role}.`;

  const html = renderEmailLayout({
    title: subject,
    preheader,
    company,
    contentHtml: `
      <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #111111;">Staff Invitation</h2>
      <p style="margin: 0 0 16px; color: #444444;">You have been invited to join <strong>${escapeHtml(brand)}</strong> as <strong>${escapeHtml(role)}</strong> on THREDO.</p>

      <div style="text-align: center; margin: 32px 0;">
        <a href="${escapeHtml(acceptUrl)}" style="background-color: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-size: 14px; font-weight: 600; display: inline-block;">Accept Invitation</a>
      </div>

      <p style="margin: 0 0 12px; font-size: 12px; color: #888888; text-align: center;">This invitation link is valid for 72 hours and can only be used once.</p>
      <p style="margin: 0; font-size: 11px; color: #AAAAAA; word-break: break-all; text-align: center;">If the button does not work, copy and paste this URL into your browser:<br>${escapeHtml(acceptUrl)}</p>
    `,
  });

  const text = `STAFF INVITATION - ${brand}
You have been invited to join ${brand} as ${role}.

Accept your invitation here:
${acceptUrl}

This link is valid for 72 hours and can only be used once.`;

  return { subject, preheader, html, text };
}
"""

with open('/Users/ceooctapus/mehar/base44/shared/emailTemplates.js', 'w', encoding='utf-8') as f:
    f.write(code)
print('emailTemplates.js written successfully')
