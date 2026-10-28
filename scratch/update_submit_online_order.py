file_path = '/Users/ceooctapus/mehar/base44/functions/submitOnlineOrder/entry.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
old_import = "import { computeAccessState } from '../../shared/access.js';"
new_import = """import { computeAccessState } from '../../shared/access.js';
import { sendEmail } from '../../shared/mailer.js';
import { onlineOrderReceivedEmail } from '../../shared/emailTemplates.js';"""

if "shared/mailer.js" not in content:
    content = content.replace(old_import, new_import, 1)

# Tailoring email dispatch
old_tailoring_return = "return Response.json({ ok: true, reference: orderId, review: !autoAccept });"
new_tailoring_return = """// Email confirmation to customer if email provided
      const targetEmail = cust.email || customer.email;
      if (targetEmail && typeof targetEmail === 'string' && targetEmail.includes('@')) {
        try {
          const template = onlineOrderReceivedEmail({
            orderId,
            orderType: 'tailoring',
            customerName: cust.name,
            total: null,
            company,
          });
          await sendEmail({
            to: targetEmail.trim(),
            subject: template.subject,
            html: template.html,
            text: template.text,
            idempotencyKey: `order:${orderId}`,
            templateName: 'online_order_received',
          });
        } catch (emErr) {
          console.warn('[submitOnlineOrder] Email confirmation failed:', emErr);
        }
      }

      return Response.json({ ok: true, reference: orderId, review: !autoAccept });"""

# Retail email dispatch
old_retail_return = "return Response.json({ ok: true, reference: saleId, review: !autoAccept });"
new_retail_return = """// Email confirmation to customer if email provided
      const retailEmail = cust.email || customer.email;
      if (retailEmail && typeof retailEmail === 'string' && retailEmail.includes('@')) {
        try {
          const template = onlineOrderReceivedEmail({
            orderId: saleId,
            orderType: 'retail',
            customerName: cust.name,
            total: subtotal,
            company,
          });
          await sendEmail({
            to: retailEmail.trim(),
            subject: template.subject,
            html: template.html,
            text: template.text,
            idempotencyKey: `order:${saleId}`,
            templateName: 'online_order_received',
          });
        } catch (emErr) {
          console.warn('[submitOnlineOrder] Email confirmation failed:', emErr);
        }
      }

      return Response.json({ ok: true, reference: saleId, review: !autoAccept });"""

if old_tailoring_return in content:
    content = content.replace(old_tailoring_return, new_tailoring_return, 1)

if old_retail_return in content:
    content = content.replace(old_retail_return, new_retail_return, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('submitOnlineOrder/entry.ts updated successfully')
