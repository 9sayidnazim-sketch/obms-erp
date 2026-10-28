import json

# 1. Update User.jsonc
user_jsonc_path = '/Users/ceooctapus/mehar/base44/entities/User.jsonc'
user_data = {
  "name": "User",
  "type": "object",
  "properties": {
    "role": {
      "type": "string",
      "description": "The role of the user in the app",
      "enum": [
        "admin",
        "manager",
        "tailor",
        "user"
      ],
      "default": "user"
    },
    "business_id": {
      "type": "string",
      "description": "Tenant business ID"
    },
    "full_name": {
      "type": "string",
      "description": "User's full name"
    },
    "phone": {
      "type": "string",
      "description": "User's phone number in E.164 format"
    }
  },
  "required": [
    "role"
  ]
}

with open(user_jsonc_path, 'w', encoding='utf-8') as f:
    json.dump(user_data, f, indent=2)
print('User.jsonc updated')

# 2. Create StaffInvitation.jsonc
invite_jsonc_path = '/Users/ceooctapus/mehar/base44/entities/StaffInvitation.jsonc'
invite_data = {
  "name": "StaffInvitation",
  "type": "object",
  "properties": {
    "business_id": {
      "type": "string",
      "description": "The business inviting the staff member"
    },
    "email": {
      "type": "string",
      "description": "Invitee email address (lowercase)"
    },
    "role": {
      "type": "string",
      "enum": [
        "admin",
        "manager",
        "tailor",
        "user"
      ],
      "default": "user"
    },
    "token_hash": {
      "type": "string",
      "description": "SHA-256 hash of the 32-byte secret invitation token"
    },
    "status": {
      "type": "string",
      "enum": [
        "pending",
        "accepted",
        "revoked",
        "expired"
      ],
      "default": "pending"
    },
    "expires_at": {
      "type": "string",
      "description": "ISO 8601 timestamp (72 hours from creation)"
    },
    "attempt_count": {
      "type": "number",
      "default": 1
    },
    "invited_by_user_id": {
      "type": "string",
      "description": "ID of administrator who issued invitation"
    },
    "accepted_by_user_id": {
      "type": "string",
      "description": "ID of user who accepted invitation"
    },
    "accepted_at": {
      "type": "string",
      "description": "ISO timestamp when accepted"
    }
  },
  "required": [
    "business_id",
    "email",
    "role",
    "token_hash",
    "status",
    "expires_at"
  ]
}

with open(invite_jsonc_path, 'w', encoding='utf-8') as f:
    json.dump(invite_data, f, indent=2)
print('StaffInvitation.jsonc created')

# 3. Create base44/shared/invitations.js
shared_invitations_code = """// Shared Staff Invitations Helper for THREDO (Base44 & Vercel)
// Handles cryptographic token generation, SHA-256 hashing, and rate limiting

import { validateEmail } from './mailer.js';

export const ALLOWED_ROLES = ['admin', 'manager', 'tailor', 'user'];

/**
 * Computes SHA-256 hex string for a secret token
 * Supports Web Crypto API (Deno, browsers, modern Node) and Node crypto fallback
 */
export async function hashToken(token) {
  if (!token || typeof token !== 'string') return '';
  const encoder = new TextEncoder();
  const data = encoder.encode(token.trim());

  if (typeof crypto !== 'undefined' && crypto.subtle && typeof crypto.subtle.digest === 'function') {
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
  }

  // Node.js fallback
  try {
    const { createHash } = await import('node:crypto');
    return createHash('sha256').update(token.trim()).digest('hex');
  } catch (_) {
    throw new Error('No cryptographic hashing support available in environment');
  }
}

/**
 * Generates a cryptographically random 32-byte hex token (64 characters)
 */
export function generateInvitationToken() {
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    const bytes = new Uint8Array(32);
    crypto.getRandomValues(bytes);
    return Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
  }
  // Math.random fallback for test environments without crypto
  return Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
}

// In-memory rate limiting: max 10 invites per business per hour
const inviteRateLimits = new Map();

export function checkInviteRateLimit(businessId) {
  const now = Date.now();
  const windowMs = 60 * 60 * 1000; // 1 hour
  const record = inviteRateLimits.get(businessId) || [];
  const recent = record.filter((t) => now - t < windowMs);

  if (recent.length >= 10) {
    return {
      allowed: false,
      waitMinutes: Math.ceil((recent[0] + windowMs - now) / 60000),
    };
  }

  recent.push(now);
  inviteRateLimits.set(businessId, recent);
  return { allowed: true };
}

export function resetInviteRateLimits() {
  inviteRateLimits.clear();
}
"""

with open('/Users/ceooctapus/mehar/base44/shared/invitations.js', 'w', encoding='utf-8') as f:
    f.write(shared_invitations_code)
print('base44/shared/invitations.js created')
