file_path = '/Users/ceooctapus/mehar/base44/functions/sendSaleBill/entry.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check imports
old_import = "import { getDefaultCompany, companyName } from '../../shared/company.js';"
new_import = """import { getDefaultCompany, companyName } from '../../shared/company.js';
import { buildSaleBillPdf } from '../../shared/pdfInvoice.js';
import { sendEmail } from '../../shared/mailer.js';
import { invoiceEmail } from '../../shared/emailTemplates.js';"""

if "shared/pdfInvoice.js" not in content:
    content = content.replace(old_import, new_import, 1)

# In the body, replace:
# const pdfBytes = buildSaleBillPdf(sale, company);
# with pdfResult
old_pdf_call = "const pdfBytes = buildSaleBillPdf(sale, company);"
new_pdf_call = """const pdfResult = buildSaleBillPdf(sale, company, jsPDF);
    const pdfBytes = pdfResult.arrayBuffer;

    // Email invoice dispatch via Resend
    let emailResult = null;
    const customerEmail = body.customer_email || body.email || sale.customer_email;
    if (customerEmail && typeof customerEmail === 'string' && customerEmail.includes('@')) {
      const alreadySentEmail = sale.bill_sent_email === true;
      const forceEmail = Boolean(body.force_email_resend || body.force_retry || body.dev_simulate);
      if (!alreadySentEmail || forceEmail) {
        try {
          const template = invoiceEmail({ sale, company });
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
            secrets,
          });

          const emailHistoryItem = {
            recipient: customerEmail.trim(),
            invoice_id: invoiceNo,
            timestamp: new Date().toISOString(),
            message_id: emailRes.id || null,
            status: emailRes.ok ? 'Sent' : 'Failed',
            error: emailRes.error || null,
          };

          const updatedEmailHistory = [
            emailHistoryItem,
            ...(Array.isArray(sale.email_history) ? sale.email_history : [])
          ];

          await db.asServiceRole.entities.Sale.update(sale.id, {
            email_recipient: customerEmail.trim(),
            email_status: emailRes.ok ? 'Sent' : 'Failed',
            email_history: updatedEmailHistory,
            bill_sent_email: emailRes.ok ? true : Boolean(sale.bill_sent_email),
          }).catch(() => {});

          emailResult = {
            ok: emailRes.ok,
            id: emailRes.id || null,
            status: emailRes.ok ? 'Sent' : 'Failed',
            error: emailRes.error || null,
          };
        } catch (emErr) {
          console.warn('[sendSaleBill] Email dispatch error:', emErr);
          emailResult = { ok: false, error: emErr.message };
        }
      } else {
        emailResult = { ok: true, status: 'Already Sent (Skipped)' };
      }
    }"""

if old_pdf_call in content:
    content = content.replace(old_pdf_call, new_pdf_call, 1)

# Remove local function money and buildSaleBillPdf
idx_money = content.find('\nfunction money(n) {')
if idx_money != -1:
    content = content[:idx_money].rstrip() + '\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('sendSaleBill/entry.ts updated successfully')
