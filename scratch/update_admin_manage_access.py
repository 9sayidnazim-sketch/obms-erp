file_path = '/Users/ceooctapus/mehar/base44/functions/adminManageAccess/entry.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
old_import = "import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';"
new_import = """import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';
import { sendEmail } from '../../shared/mailer.js';
import { accessRevokedEmail } from '../../shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../shared/company.js';"""

if "shared/mailer.js" not in content:
    content = content.replace(old_import, new_import, 1)

old_notif = """      try {
        await svc.entities.AppNotification.create({
          business_id,
          type: 'access_revoked',
          title: 'Access Revoked',
          message: reason ? `Access was revoked: ${reason}` : 'Access was revoked by administrator.',
          dedupe_key: `notif-revoked-${business_id}-${Date.now()}`,
          link: '/paywall',
          is_read: false,
          created_date: now.toISOString()
        });
      } catch (e) {}"""

new_notif = """      const dedupeKey = `notif-revoked-${business_id}-${Date.now()}`;
      try {
        await svc.entities.AppNotification.create({
          business_id,
          type: 'access_revoked',
          title: 'Access Revoked',
          message: reason ? `Access was revoked: ${reason}` : 'Access was revoked by administrator.',
          dedupe_key: dedupeKey,
          link: '/paywall',
          is_read: false,
          created_date: now.toISOString()
        });
      } catch (e) {}

      try {
        const company = await getDefaultCompany(base44);
        const businessEmail = company?.email || 'billing@mail.SENDING_DOMAIN';
        const template = accessRevokedEmail({
          businessName: companyName(company),
          reason: reason || 'Access was revoked by administrator.',
          company,
        });
        await sendEmail({
          to: businessEmail,
          subject: template.subject,
          html: template.html,
          text: template.text,
          idempotencyKey: dedupeKey,
          templateName: 'access_revoked',
        });
      } catch (emErr) {
        console.warn('[adminManageAccess] Email dispatch failed:', emErr);
      }"""

if old_notif in content:
    content = content.replace(old_notif, new_notif, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('adminManageAccess/entry.ts updated')
