# Feature Spec: Account Creation & Login
## Product: Mexican Online Stock Trading Retail Brokerage

### Document info
- Owner: Product / Engineering
- Status: Draft
- Last updated: 2026-03-03

---

## 1. Overview (context)
This application is a Mexican retail brokerage that enables individuals in Mexico to open an investment account, fund it, and trade listed securities through a web and mobile experience. The product must maximize trust and safety, minimize onboarding friction, and meet Mexico-appropriate compliance and security expectations.

**Primary user outcomes**
- A user can create an account quickly and safely.
- A user can sign in reliably across devices.
- The platform protects accounts from takeover and fraud.
- The platform maintains clear audit trails for security and compliance.

**Non-functional priorities**
1. Security and account protection
2. Reliability and recovery (users must not get locked out)
3. Speed of onboarding (low friction, high completion)
4. Clarity and trust (transparent steps, minimal confusion)

---

## 2. Scope (this spec)
### In scope (minimum viable product)
- Create an application account and sign in using:
  1) Email address (magic link and/or password)
  2) Google sign-in
  3) Apple sign-in (recommended for mobile users)
  4) Passkeys (recommended default when available)
  5) Phone number verification (SMS) as fallback for recovery and optional sign-in
- Add two-step verification for high-risk actions and optionally for every login
- Session management (device sessions, logout, session expiration)
- Account recovery flows (email, phone fallback, support escalation)
- Security controls (rate limits, suspicious login detection, device trust, audit logs)

### Explicitly out of scope (handled by separate specs)
- Identity verification (know-your-customer), document upload, selfie checks
- Suitability questionnaires and risk profiling
- Funding (bank transfers), deposits/withdrawals
- Trading permissions, market data entitlements
- Customer support tooling beyond basic escalation notes

---

## 3. Users and entry points
### User types
- New retail user in Mexico (first-time account creation)
- Returning retail user (repeat sign-in)
- Locked-out user (recovery)
- User upgrading security (enabling passkeys and two-step verification)

### Entry points
- Web and mobile landing page “Create account”
- Mobile deep links from marketing campaigns
- “Sign in” from header
- Re-authentication prompts for sensitive actions (funding, withdrawals, trading, profile changes)

---

## 4. Goals and success metrics
### Goals
- High completion rate for account creation
- Low support tickets for login/recovery
- Low account takeover rate
- Clear security posture without heavy friction

### Success metrics (initial targets)
- Account creation completion rate: target defined by product
- Sign-in success rate: target defined by product
- Two-step verification enrollment: target defined by product
- Account takeover events: near zero; investigated and tracked

---

## 5. Authentication methods (requirements)
### 5.1 Email-based sign-up and login
**Requirement**
- User can create an account with an email address.
- Offer one of the following as default:
  - Magic link to email (recommended for usability)
  - Password option (allowed, but discourage weak passwords)
- Support email verification during sign-up.

**Details**
- Email verification required before enabling trading-related actions (or before full access; decide in policy).
- If password is offered:
  - Must enforce strong password requirements
  - Must have breached-password checks (if service available)
  - Must support password reset via email

### 5.2 Google sign-in
**Requirement**
- User can create account and log in using Google sign-in.
- Must support account linking: if a user previously registered with email and later uses Google with same email, provide a safe linking flow (do not auto-link without verification).

### 5.3 Apple sign-in
**Requirement**
- User can create account and log in using Apple sign-in.
- Support Apple private relay email addresses.
- Support account linking similar to Google.

### 5.4 Passkeys
**Requirement**
- Offer passkeys as a primary, strongly recommended option when supported.
- Passkeys can be set up:
  - Immediately after account creation, or
  - On first successful login (prompt to upgrade)
- Support multiple passkeys per account (for multiple devices).

### 5.5 Phone number verification (SMS) and WhatsApp consideration
**Requirement**
- Collect phone number optionally at onboarding or during security setup.
- Use SMS one-time codes as a fallback for:
  - Recovery
  - Two-step verification when a stronger method is not available
- If WhatsApp verification is considered:
  - Only if supported by a reputable verification provider
  - Must include anti-sim-swap and anti-social-engineering safeguards
  - Must never be the only recovery method

**Note**
Phone-based methods are convenient in Mexico, but they are weaker than passkeys or authenticator apps. Treat phone as fallback, not the core security method.

---

## 6. Two-step verification (two-factor authentication) policy
### 6.1 Enrollment
- After first login, prompt the user to enable two-step verification.
- Provide at least:
  - Authenticator app codes (recommended)
  - Passkeys (strong alternative)
  - SMS fallback (last resort)

### 6.2 Enforcement
Two-step verification required for:
- Changing email address
- Changing phone number
- Changing password (if passwords exist)
- Adding or removing passkeys
- Withdrawing funds (when funding exists)
- Changing bank accounts (when funding exists)
- Viewing or exporting sensitive account statements (policy decision)

Optional policy:
- Require two-step verification on every login for high-risk accounts or suspicious logins.

### 6.3 Recovery codes
- Provide one-time recovery codes at enrollment.
- Encourage user to store them safely.
- Allow regenerating recovery codes only after re-authentication.

---

## 7. Account creation flow (user experience)
### 7.1 Create account (happy path)
1. User chooses sign-up method:
   - Email
   - Google
   - Apple
2. If email:
   - User enters email
   - User receives verification (magic link or code)
3. After first successful authentication:
   - Collect required profile fields (minimum):
     - Full name (legal name field can be later in identity verification)
     - Country of residence (default Mexico)
     - Acceptance of terms and privacy notice
   - Prompt to set up passkeys and two-step verification
4. User lands in the application home (with clear next steps such as identity verification and funding, handled in separate specs).

### 7.2 Abandonment handling
- Save partial progress
- If user returns via same sign-in method, continue onboarding

---

## 8. Login flow (user experience)
### 8.1 Sign in (happy path)
- User chooses method:
  - Passkey (if available)
  - Google / Apple
  - Email
- After login:
  - If risk is high (new device, unusual location, too many attempts), require two-step verification
  - If low risk and user opted out, allow standard login

### 8.2 Suspicious login handling
- Show neutral message: “We could not sign you in” without revealing whether the email exists.
- Trigger additional verification challenges.
- Notify user via email of new device sign-in.

---

## 9. Session and device management
### Requirements
- Sessions expire after a defined period (policy decision; include “remember me” with caution).
- Allow user to view active sessions/devices:
  - Device name
  - Last active time
  - Approximate location
- Allow user to revoke sessions (log out of other devices).

---

## 10. Account recovery
### Recovery methods
- Email recovery (primary)
- Passkey re-registration if existing trusted session exists
- Phone (SMS) fallback if previously verified
- Support escalation path:
  - Identity re-verification (separate policy/spec)
  - Manual review with audit trail

### Requirements
- Recovery flow must be resistant to social engineering:
  - Step-up verification required
  - Cooling-off period for changing critical identifiers (email/phone) if risk detected
  - Notify user of recovery attempts

---

## 11. Security and abuse prevention requirements
- Rate limiting and lockouts:
  - Per account identifier and per internet address
- Bot protection during sign-up
- Detect credential stuffing (if passwords exist)
- Detect and challenge suspicious behavior:
  - Multiple failed attempts
  - New device + unusual region
  - Rapid sign-in method switching
- Audit logs:
  - Sign-up events
  - Sign-in events
  - Two-step verification events
  - Recovery events
  - Account identifier changes

---

## 12. Compliance and privacy notes
- Store minimal personal data until identity verification is required.
- Encrypt sensitive data at rest and in transit.
- Maintain auditable security event records.
- Terms and privacy notice must be accepted during onboarding.

---

## 13. Acceptance criteria (testable)
### Account creation
- A user can create an account via email and complete verification.
- A user can create an account via Google.
- A user can create an account via Apple.
- A user can set up a passkey after account creation.
- A user can enable two-step verification and receive recovery codes.

### Login
- A user can sign in with the same method used at sign-up.
- A user can sign in with a passkey on a supported device.
- A new device sign-in triggers a security notification.
- Suspicious login attempts trigger step-up verification.

### Recovery
- A user can recover access using email.
- A user with a verified phone can use SMS as fallback recovery.
- Users cannot change email or phone without re-authentication and step-up verification.

### Security
- The system does not reveal whether an email address is registered.
- Rate limiting prevents repeated brute force attempts.

---

## 14. Open questions (to resolve before implementation)
- Do we allow access to non-trading parts of the application before identity verification? yes
- Do we require two-step verification for every login, or only for high-risk events? no
- Is phone number required at onboarding or optional until later? no
- Do we support WhatsApp verification at all, or only SMS? yes whatsapp
- What is the default session expiration duration? 1 hour

---
