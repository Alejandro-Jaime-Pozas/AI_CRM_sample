# ADR 0001: Authentication Strategy - Passkey-First & JWT Sessions

## Status
**Proposed**

## Context
The "Mexican Online Stock Trading Retail Brokerage" requires a security-first approach to protect user accounts and financial data. Traditional passwords are prone to phishing, credential stuffing, and reuse.

The current architecture specifies:
- Frontend: Next.js (App Router)
- Backend: Django (Django REST Framework)
- Authentication: django auth + JWT (Simple JWT)

The product overview specifically states:
- "Passkeys preferred over passwords."
- "Security first (prevent account takeover and fraud)."

However, there is no detailed plan on how Passkeys (WebAuthn) and Social Logins (Google/Apple) will integrate with the Django + Simple JWT architecture while maintaining a passwordless experience.

## Decision
We will adopt a **Passkey-First** and **Passwordless** authentication strategy:

1.  **Primary Authentication**: WebAuthn (Passkeys) will be the recommended login method.
2.  **Fallback/Onboarding**: Email Magic Links will be used for users on devices that do not support Passkeys or as a secondary verification step during onboarding.
3.  **Social Login**: Google and Apple Sign-In will be supported as alternative primary methods.
4.  **Session Management**:
    - Upon successful authentication via WebAuthn, OAuth2, or Magic Link, the Django backend will issue a JSON Web Token (JWT) using `djangorestframework-simplejwt`.
    - JWTs will be used to authorize all subsequent API requests.
5.  **No Passwords**: We will not collect or store passwords for retail users by default. This eliminates a major attack vector.
6.  **Recovery**: A combination of Email Magic Links and SMS/WhatsApp-based two-step verification will be used for account recovery.

## Consequences
- **Security**: Significantly reduced risk of account takeover via phishing or credential leaks.
- **UX**: Lower friction for users (biometric login).
- **Complexity**: Backend must implement WebAuthn challenge/response logic (e.g., using `django-passkeys` or similar).
- **Dependencies**: New backend dependencies for WebAuthn and Magic Link generation.
- **Compliance**: Aligns with modern security standards for financial institutions.
- **Auditability**: Clear audit trail for every distinct authentication method used.

## Alternatives Considered
- **Standard Django Passwords**: Rejected due to lower security and higher friction.
- **Third-party Auth Providers (e.g., Auth0, Firebase)**: Rejected to keep auth logic in-house for better control over user data and compliance logs, as per current architecture.
