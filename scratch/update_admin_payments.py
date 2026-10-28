# 1. Update adminApprovePayment/entry.ts
approve_path = '/Users/ceooctapus/mehar/base44/functions/adminApprovePayment/entry.ts'
with open(approve_path, 'r', encoding='utf-8') as f:
    approve_content = f.read()

old_approve_import = "import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';"
new_approve_import = """import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';
import { sendEmail } from '../../shared/mailer.js';
import { paymentApprovedEmail } from '../../shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../shared/company.js';"""

if "shared/mailer.js" not in approve_content:
    approve_content = approve_content.replace(old_approve_import, new_approve_import, 1)

old_approve_notif = """    // 5. Notify user
    try {
      await svc.entities.AppNotification.create({
        business_id: businessId,
        user_id: submission.user_id,
        type: 'subscription_active',
        title: 'Payment Verified & Approved',
        message: `Your payment was verified. Subscription is active until ${newExpiresAt.slice(0, 10)}.`,
        dedupe_key: `notif-verified-${submission.id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (e) {}"""

new_approve_notif = """    // 5. Notify user & Email business
    try {
      await svc.entities.AppNotification.create({
        business_id: businessId,
        user_id: submission.user_id,
        type: 'subscription_active',
        title: 'Payment Verified & Approved',
        message: `Your payment was verified. Subscription is active until ${newExpiresAt.slice(0, 10)}.`,
        dedupe_key: `notif-verified-${submission.id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (e) {}

    try {
      const company = await getDefaultCompany(base44);
      const businessEmail = company?.email || 'billing@mail.SENDING_DOMAIN';
      const template = paymentApprovedEmail({
        businessName: companyName(company),
        planName: submission.plan_name || 'Active Subscription Plan',
        expiresAt: newExpiresAt,
        company,
      });
      await sendEmail({
        to: businessEmail,
        subject: template.subject,
        html: template.html,
        text: template.text,
        idempotencyKey: `notif-verified-${submission.id}`,
        templateName: 'payment_approved',
      });
    } catch (emErr) {
      console.warn('[adminApprovePayment] Email dispatch failed:', emErr);
    }"""

if old_approve_notif in approve_content:
    approve_content = approve_content.replace(old_approve_notif, new_approve_notif, 1)

with open(approve_path, 'w', encoding='utf-8') as f:
    f.write(approve_content)
print('adminApprovePayment/entry.ts updated')

# 2. Update adminRejectPayment/entry.ts
reject_path = '/Users/ceooctapus/mehar/base44/functions/adminRejectPayment/entry.ts'
with open(reject_path, 'r', encoding='utf-8') as f:
    reject_content = f.read()

old_reject_import = "import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';"
new_reject_import = """import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';
import { sendEmail } from '../../shared/mailer.js';
import { paymentRejectedEmail } from '../../shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../shared/company.js';"""

if "shared/mailer.js" not in reject_content:
    reject_content = reject_content.replace(old_reject_import, new_reject_import, 1)

old_reject_notif = """    // Notify user
    try {
      await svc.entities.AppNotification.create({
        business_id: submission.business_id,
        user_id: submission.user_id,
        type: 'payment_rejected',
        title: 'Payment Verification Rejected',
        message: `Your payment reference was rejected: ${reason.trim()}. You may submit a new reference.`,
        dedupe_key: `notif-rejected-${submission.id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (e) {}"""

new_reject_notif = """    // Notify user & Email business
    try {
      await svc.entities.AppNotification.create({
        business_id: submission.business_id,
        user_id: submission.user_id,
        type: 'payment_rejected',
        title: 'Payment Verification Rejected',
        message: `Your payment reference was rejected: ${reason.trim()}. You may submit a new reference.`,
        dedupe_key: `notif-rejected-${submission.id}`,
        link: '/paywall',
        is_read: false,
        created_date: now.toISOString()
      });
    } catch (e) {}

    try {
      const company = await getDefaultCompany(base44);
      const businessEmail = company?.email || 'billing@mail.SENDING_DOMAIN';
      const template = paymentRejectedEmail({
        businessName: companyName(company),
        referenceNumber: submission.reference_number || submission.id,
        reason: reason.trim(),
        company,
      });
      await sendEmail({
        to: businessEmail,
        subject: template.subject,
        html: template.html,
        text: template.text,
        idempotencyKey: `notif-rejected-${submission.id}`,
        templateName: 'payment_rejected',
      });
    } catch (emErr) {
      console.warn('[adminRejectPayment] Email dispatch failed:', emErr);
    }"""

if old_reject_notif in reject_content:
    reject_content = reject_content.replace(old_reject_notif, new_reject_notif, 1)

with open(reject_path, 'w', encoding='utf-8') as f:
    f.write(reject_content)
print('adminRejectPayment/entry.ts updated')
