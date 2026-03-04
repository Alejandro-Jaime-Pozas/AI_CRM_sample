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
1. Security and account protection (Passkey-first policy)
2. Reliability and recovery (users must not get locked out)
3. Speed of onboarding (progressive disclosure)
4. Clarity and trust (transparent steps)

---

## 2. Scope (this spec)
### In scope (minimum viable product)
- **Account Creation**: Sign up via Email, Google, or Apple.
- **Authentication**:
  - Primary: Passkeys (WebAuthn).
  - Secondary: Email Magic Links.
  - Social: Google Sign-In, Apple Sign-In.
- **Phone Verification**: SMS/WhatsApp for recovery and secondary verification.
- **Two-Step Verification (2SV)**: Enrollment and enforcement for high-risk actions.
- **Session Management**: Device-specific sessions, logout, and 1-hour expiration.
- **Account Recovery**: Email-based recovery with phone fallback.
- **Audit Logging**: Mandatory logging of all auth-related events.

### Explicitly out of scope
- Full KYC (Identity verification) - *Handled in separate spec*.
- Risk profiling (Suitability) - *Handled in separate spec*.
- Financial transactions (Funding/Trading).

---

## 3. Business Rules
1. **Age Requirement**: Users must be 18+ (verified during KYC, but initial self-attestation at sign-up).
2. **Residency**: Primary focus is Mexican residents.
3. **Single Identity**: One account per unique CURP (checked later in KYC), but for Auth, one account per unique email.
4. **Email Ownership**: Mandatory verification before account activation.
5. **Progressive Disclosure**: Only collect essential data (Name, Email) before KYC step.

---

## 4. Authentication Methods
### 4.1 Passkeys (Preferred)
- Default recommendation for all supported devices.
- Support for multiple passkeys (e.g., phone and laptop).
- Biometric-backed security.

### 4.2 OAuth (Google & Apple)
- Seamless integration for mobile and web.
- Mandatory account linking check (verify email ownership if already registered).

### 4.3 Email Magic Links
- Passwordless experience to reduce friction and eliminate password-related vulnerabilities.
- Fallback for devices not supporting Passkeys.

### 4.4 SMS / WhatsApp Fallback
- Used primarily for recovery and step-up authentication.
- WhatsApp is preferred in the Mexican market for higher delivery reliability.

---

## 5. Security Requirements
1. **Passkey-First**: Prompt for passkey creation immediately after first login.
2. **Rate Limiting**: IP-based and identifier-based throttling for all auth endpoints.
3. **Session Expiry**: 1-hour idle timeout; absolute timeout of 24 hours.
4. **Encryption**: All PII and auth tokens encrypted at rest (Postgres/Redis) and in transit (TLS 1.2+).
5. **Audit Trail**: Every login attempt (success/failure) must be logged with timestamp, IP, and device fingerprint.

---

## 6. Acceptance Criteria
- [ ] User can create an account using GMail/Apple and be redirected to dashboard.
- [ ] User can register a Passkey and use it for subsequent logins.
- [ ] User receives an email magic link if Passkey is unavailable.
- [ ] Suspicious login (new IP/Device) triggers a notification to the user.
- [ ] 2SV is required before a user can change their contact email.
- [ ] All auth events are visible in the system audit logs.

---

## 7. Open Questions
- **Q**: What specific magic link provider will be used? (Decision: Custom Django implementation with signed URLs).
- **Q**: Should we enforce 2SV for *every* login during MVP? (Decision: High-risk only, but optional for users).
- **Q**: How long is the "cooling-off" period for email changes? (Decision: 24 hours).
