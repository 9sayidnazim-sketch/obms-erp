file_path = '/Users/ceooctapus/mehar/api/functions/sendSaleBill.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
old_import = "import { checkOrbitStatus, sendOrbitMediaDocument } from '../../base44/shared/whatsapp.js';"
new_import = """import { checkOrbitStatus, sendOrbitMediaDocument } from '../../base44/shared/whatsapp.js';
import { buildSaleBillPdf } from '../../base44/shared/pdfInvoice.js';
import { sendEmail } from '../../base44/shared/mailer.js';
import { invoiceEmail } from '../../base44/shared/emailTemplates.js';"""

if "base44/shared/pdfInvoice.js" not in content:
    content = content.replace(old_import, new_import, 1)

# Target the manual doc creation:
start_doc = "    const doc = new jsPDF({ unit: 'mm', format: 'a4' });"
end_caption = "    const caption = `Hello ${custName}, here is your invoice ${invoiceNo}. Thank you for choosing THREDO!`;"

idx_start = content.find(start_doc)
idx_end = content.find(end_caption)

if idx_start != -1 and idx_end != -1:
    end_pos = idx_end + len(end_caption)
    replacement = """    const invoiceNo = sale.sale_id || invoiceId;
    const custName = sale.customer_name || 'Customer';
    const pdfResult = buildSaleBillPdf(sale, null, jsPDF);
    const pdfBytes = pdfResult.arrayBuffer;
    const fileName = pdfResult.fileName;
    const caption = `Hello ${custName}, here is your invoice ${invoiceNo}. Thank you for choosing THREDO!`;

    // Email invoice dispatch via Resend
    let emailResult = null;
    const customerEmail = body.customer_email || body.email || sale.customer_email;
    if (customerEmail && typeof customerEmail === 'string' && customerEmail.includes('@')) {
      const alreadySentEmail = sale.bill_sent_email === true;
      const forceEmail = Boolean(body.force_email_resend || body.force_retry);
      if (!alreadySentEmail || forceEmail) {
        try {
          const template = invoiceEmail({ sale, company: null });
          const emailRes = await sendEmail({
            to: customerEmail.trim(),
            subject: template.subject,
            html: template.html,
            text: template.text,
            attachments: [
              {
                filename: pdfResult.fileName,
                content: pdfResult.base64,
              }
            ],
            idempotencyKey: `invoice:${invoiceNo}:${forceEmail ? Date.now() : '1'}`,
            templateName: 'invoice',
          });
          emailResult = {
            ok: emailRes.ok,
            id: emailRes.id || null,
            status: emailRes.ok ? 'Sent' : 'Failed',
            error: emailRes.error || null,
          };
        } catch (emErr) {
          console.warn('[api/sendSaleBill] Email dispatch error:', emErr);
          emailResult = { ok: false, error: emErr.message };
        }
      } else {
        emailResult = { ok: true, status: 'Already Sent (Skipped)' };
      }
    }"""
    content = content[:idx_start] + replacement + content[end_pos:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('api/functions/sendSaleBill.js updated successfully')
