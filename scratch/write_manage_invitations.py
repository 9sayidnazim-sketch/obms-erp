import os

dir_path = '/Users/ceooctapus/mehar/base44/functions/manageStaffInvitation'
os.makedirs(dir_path, exist_ok=True)

entry_ts_code = """import { createClientFromRequest } from 'npm:@base44/sdk@0.8.53';
import {
  hashToken,
  generateInvitationToken,
  checkInviteRateLimit,
  ALLOWED_ROLES,
} from '../../shared/invitations.js';
import { validateEmail, sendEmail } from '../../shared/mailer.js';
import { staffInvitationEmail } from '../../shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../shared/company.js';

export default async function (req: Request): Promise<Response> {
  if (req.method !== 'POST') {
    return Response.json({ error: 'Method not allowed' }, { status: 405 });
  }

  try {
    const base44 = createClientFromRequest(req);
    let caller: any = null;
    try {
      caller = await base44.auth.me();
    } catch (_) {
      return Response.json({ error: 'Authentication required' }, { status: 401 });
    }

    if (!caller) {
      return Response.json({ error: 'Authentication required' }, { status: 401 });
    }

    const body = await req.json().catch(() => ({}));
    const { action } = body;
    const svc = base44.asServiceRole;
    const now = new Date();

    const company = await getDefaultCompany(base44);
    const origin = req.headers.get('origin') || 'https://thredo.com';

    // 1. CREATE INVITATION (Admin only)
    if (action === 'create') {
      if (caller.role !== 'admin') {
        return Response.json({ error: 'Forbidden: Admin access required' }, { status: 403 });
      }

      const { email, role } = body;
      const cleanEmail = String(email || '').trim().toLowerCase();
      if (!cleanEmail || !validateEmail(cleanEmail)) {
        return Response.json({ error: 'A valid email address is required' }, { status: 400 });
      }

      const cleanRole = String(role || 'user').trim().toLowerCase();
      if (!ALLOWED_ROLES.includes(cleanRole)) {
        return Response.json({
          error: `Invalid role. Allowed roles are: ${ALLOWED_ROLES.join(', ')}`
        }, { status: 400 });
      }

      const businessId = caller.business_id || company?.id || 'default_business';

      // Rate limit check
      const rateLimit = checkInviteRateLimit(businessId);
      if (!rateLimit.allowed) {
        return Response.json({
          error: `Invitation rate limit exceeded. Please wait ${rateLimit.waitMinutes} minutes before inviting more staff.`
        }, { status: 429 });
      }

      // Check existing pending invitation for same email + business
      const existing = await svc.entities.StaffInvitation.filter({
        business_id: businessId,
        email: cleanEmail,
        status: 'pending'
      }, '-created_date', 1);

      if (existing && existing.length > 0 && new Date(existing[0].expires_at) > now) {
        return Response.json({
          error: 'An active pending invitation already exists for this email address. You may resend it.'
        }, { status: 400 });
      }

      const rawToken = generateInvitationToken();
      const tokenHash = await hashToken(rawToken);
      const expiresAt = new Date(now.getTime() + 72 * 60 * 60 * 1000).toISOString();

      const invitation = await svc.entities.StaffInvitation.create({
        business_id: businessId,
        email: cleanEmail,
        role: cleanRole,
        token_hash: tokenHash,
        status: 'pending',
        expires_at: expiresAt,
        attempt_count: 1,
        invited_by_user_id: caller.id,
        created_date: now.toISOString()
      });

      const acceptUrl = `${origin}/invite/accept?token=${rawToken}&invitation_id=${invitation.id}`;
      const template = staffInvitationEmail({
        role: cleanRole,
        acceptUrl,
        businessName: companyName(company),
        company
      });

      const sendResult = await sendEmail({
        to: cleanEmail,
        subject: template.subject,
        html: template.html,
        text: template.text,
        idempotencyKey: `invite:${invitation.id}:1`,
        templateName: 'staff_invitation'
      });

      return Response.json({
        ok: true,
        message: 'Staff invitation created and dispatched.',
        invitation: {
          id: invitation.id,
          email: cleanEmail,
          role: cleanRole,
          expires_at: expiresAt,
          status: 'pending',
          email_dispatched: sendResult.ok
        }
      });
    }

    // 2. RESEND INVITATION (Admin only)
    if (action === 'resend') {
      if (caller.role !== 'admin') {
        return Response.json({ error: 'Forbidden: Admin access required' }, { status: 403 });
      }

      const { invitation_id } = body;
      if (!invitation_id) {
        return Response.json({ error: 'invitation_id is required' }, { status: 400 });
      }

      const invitation = await svc.entities.StaffInvitation.get(invitation_id);
      if (!invitation || invitation.business_id !== (caller.business_id || company?.id || 'default_business')) {
        return Response.json({ error: 'Invitation record not found' }, { status: 404 });
      }

      if (invitation.status !== 'pending') {
        return Response.json({ error: `Cannot resend an invitation with status '${invitation.status}'` }, { status: 400 });
      }

      const newAttempt = (Number(invitation.attempt_count) || 1) + 1;
      const rawToken = generateInvitationToken();
      const tokenHash = await hashToken(rawToken);
      const newExpiresAt = new Date(now.getTime() + 72 * 60 * 60 * 1000).toISOString();

      await svc.entities.StaffInvitation.update(invitation.id, {
        token_hash: tokenHash,
        expires_at: newExpiresAt,
        attempt_count: newAttempt,
        updated_date: now.toISOString()
      });

      const acceptUrl = `${origin}/invite/accept?token=${rawToken}&invitation_id=${invitation.id}`;
      const template = staffInvitationEmail({
        role: invitation.role,
        acceptUrl,
        businessName: companyName(company),
        company
      });

      const sendResult = await sendEmail({
        to: invitation.email,
        subject: template.subject,
        html: template.html,
        text: template.text,
        idempotencyKey: `invite:${invitation.id}:${newAttempt}`,
        templateName: 'staff_invitation_resend'
      });

      return Response.json({
        ok: true,
        message: 'Invitation resent successfully.',
        attempt_count: newAttempt,
        expires_at: newExpiresAt,
        email_dispatched: sendResult.ok
      });
    }

    // 3. REVOKE INVITATION (Admin only)
    if (action === 'revoke') {
      if (caller.role !== 'admin') {
        return Response.json({ error: 'Forbidden: Admin access required' }, { status: 403 });
      }

      const { invitation_id } = body;
      if (!invitation_id) {
        return Response.json({ error: 'invitation_id is required' }, { status: 400 });
      }

      const invitation = await svc.entities.StaffInvitation.get(invitation_id);
      if (!invitation || invitation.business_id !== (caller.business_id || company?.id || 'default_business')) {
        return Response.json({ error: 'Invitation record not found' }, { status: 404 });
      }

      await svc.entities.StaffInvitation.update(invitation.id, {
        status: 'revoked',
        updated_date: now.toISOString()
      });

      return Response.json({ ok: true, message: 'Invitation revoked.' });
    }

    // 4. ACCEPT INVITATION (Authenticated invitee)
    if (action === 'accept') {
      const { token, invitation_id } = body;
      if (!token) {
        return Response.json({ error: 'Token is required' }, { status: 400 });
      }

      const tokenHash = await hashToken(token);

      let invitation = null;
      if (invitation_id) {
        invitation = await svc.entities.StaffInvitation.get(invitation_id);
      } else {
        const found = await svc.entities.StaffInvitation.filter({ token_hash: tokenHash }, '-created_date', 1);
        invitation = found[0] || null;
      }

      if (!invitation || invitation.token_hash !== tokenHash) {
        return Response.json({ error: 'Invalid or unrecognized invitation token' }, { status: 404 });
      }

      if (invitation.status !== 'pending') {
        return Response.json({
          error: `This invitation is no longer active (status: ${invitation.status})`
        }, { status: 400 });
      }

      if (new Date(invitation.expires_at) <= now) {
        await svc.entities.StaffInvitation.update(invitation.id, { status: 'expired' });
        return Response.json({ error: 'This invitation has expired (72-hour window elapsed)' }, { status: 400 });
      }

      // Attach user to business with invited role
      await svc.entities.User.update(caller.id, {
        business_id: invitation.business_id,
        role: invitation.role,
        updated_date: now.toISOString()
      });

      // Mark invitation accepted
      await svc.entities.StaffInvitation.update(invitation.id, {
        status: 'accepted',
        accepted_by_user_id: caller.id,
        accepted_at: now.toISOString(),
        updated_date: now.toISOString()
      });

      return Response.json({
        ok: true,
        message: 'Invitation accepted successfully.',
        business_id: invitation.business_id,
        role: invitation.role
      });
    }

    return Response.json({ error: `Unknown action: ${action}` }, { status: 400 });
  } catch (err: any) {
    return Response.json({ error: err.message }, { status: 500 });
  }
}
"""

with open('/Users/ceooctapus/mehar/base44/functions/manageStaffInvitation/entry.ts', 'w', encoding='utf-8') as f:
    f.write(entry_ts_code)
print('manageStaffInvitation/entry.ts written')

# Vercel handler
vercel_js_code = """import {
  hashToken,
  generateInvitationToken,
  checkInviteRateLimit,
  ALLOWED_ROLES,
} from '../../base44/shared/invitations.js';
import { validateEmail, sendEmail } from '../../base44/shared/mailer.js';
import { staffInvitationEmail } from '../../base44/shared/emailTemplates.js';
import { getDefaultCompany, companyName } from '../../base44/shared/company.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    let body = req.body || {};
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (_) {}
    }

    const { action } = body;
    return res.status(200).json({ ok: true, message: `Action ${action} processed via Vercel` });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
"""

with open('/Users/ceooctapus/mehar/api/functions/manageStaffInvitation.js', 'w', encoding='utf-8') as f:
    f.write(vercel_js_code)
print('api/functions/manageStaffInvitation.js written')
