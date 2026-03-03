# Product Overview
## Mexican Online Retail Brokerage

### 1. Mission
Provide Mexican retail investors with a secure, transparent, and modern platform to open accounts, fund them, and trade publicly listed securities.

### 2. Primary User
Retail individual in Mexico who:
- Wants to invest in equities or similar instruments
- May be new to investing
- Requires high trust and clarity
- Likely uses mobile-first experiences

### 3. Core Product Principles
1. Security first (prevent account takeover and fraud)
2. Regulatory compliance
3. Clear and simple user experience
4. Gradual onboarding (progressive disclosure)
5. Transparent fees and operations

### 4. System Priorities
- All sensitive actions must require strong authentication.
- Tenant isolation is mandatory (no cross-user data exposure).
- Audit logging for all security-sensitive actions.
- Minimal personal data stored before identity verification.
- Encryption in transit and at rest.

### 5. Security Model
- Passkeys preferred over passwords.
- Two-step verification strongly encouraged.
- SMS only as fallback.
- Rate limiting and anomaly detection required.

### 6. Architecture Philosophy
- Modular services (auth, identity verification, trading, funding).
- Explicit interfaces between modules.
- Versioned APIs.
- Clear data ownership boundaries.

### 7. Out of Scope (for MVP)
- Advanced trading features
- Margin accounts
- Options trading
- Complex derivatives

### 8. Success Definition
- Users can open accounts safely.
- Users trust the platform.
- Security incidents are rare and auditable.
