file_path = '/Users/ceooctapus/mehar/base44/functions/submitPaymentReference/entry.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
old_import = "import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';"
new_import = """import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';
import { sendEmail } from '../../shared/mailer.js';
import { paymentReferenceReceivedEmail } from '../../shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../shared/company.js';"""

if "shared/mailer.js" not in content:
    content = content.replace(old_import, new_import, 1)

old_notif = """    // Create AppNotification for user (T6)
    try {
      await svc.entities.AppNotification.create({
        business_id: businessId,
        user_id: user.id,
        type: 'payment_submitted',
        title: 'Payment Reference Submitted',
        message: `Reference ${cleanRef} received. Your account is active under 48-hour provisional verification.`,
        dedupe_key: `notif-paysub-${submission_id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (notifErr) {
      console.warn('[Notification] Failed to create payment_submitted notification:', notifErr);
    }"""

new_notif = """    // Create AppNotification for user (T6) & Email notification to business
    try {
      await svc.entities.AppNotification.create({
        business_id: businessId,
        user_id: user.id,
        type: 'payment_submitted',
        title: 'Payment Reference Submitted',
        message: `Reference ${cleanRef} received. Your account is active under 48-hour provisional verification.`,
        dedupe_key: `notif-paysub-${submission_id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (notifErr) {
      console.warn('[Notification] Failed to create payment_submitted notification:', notifErr);
    }

    try {
      const company = await getDefaultCompany(base44);
      const businessEmail = company?.email || 'billing@mail.SENDING_DOMAIN';
      const template = paymentReferenceReceivedEmail({
        submissionId: submission_id,
        referenceNumber: cleanRef,
        businessName: companyName(company),
        company
      });
      await sendEmail({
        to: businessEmail,
        subject: template.subject,
        html: template.html,
        text: template.text,
        idempotencyKey: `notif-paysub-${submission_id}`,
        templateName: 'payment_reference_received'
      });
    } catch (emErr) {
      console.warn('[submitPaymentReference] Email dispatch failed:', emErr);
    }"""

if old_notif in content:
    content = content.replace(old_notif, new_notif, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('submitPaymentReference/entry.ts updated successfully')
