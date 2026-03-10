Here’s the backend shape of email + magic link auth for this spec, and how I would implement it in Django.

What the magic link is

A magic link is just a single-use, short-lived login credential delivered by email.

Instead of storing a password, the backend:

receives an email address,

creates a one-time login token,

emails a link containing that token,

verifies the token when the user clicks it,

logs the user in and creates a session,

invalidates the token so it cannot be reused.

So the email is only the delivery channel. The real auth object is the backend-issued token.

Recommended design in Django

For this product, I would not put all auth state directly inside the signed URL only.

A better production approach is:

generate a random secret token

store only its hash in the database

email the raw token to the user in the link

when the link is clicked, hash the presented token and compare to the stored hash

mark it used

create the authenticated session

This gives you:

single-use enforcement

revocation support

auditability

better control over expiry and abuse

no need to trust a stateless link forever

You can still sign the URL too, but the database-backed token is the important part.

Main data models

You already have User. Add something like this:

# backend/accounts/models.py
import hashlib
import secrets
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class MagicLinkToken(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "login", "Login"
        SIGNUP = "signup", "Signup"
        EMAIL_VERIFY = "email_verify", "Email Verify"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="magic_link_tokens",
    )
    email = models.EmailField()
    token_hash = models.CharField(max_length=64, unique=True)
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    redirect_to = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["email", "purpose", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    @staticmethod
    def generate_raw_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None
Why store both user and email

Because login attempts should be auditable against the exact email used, even if the user later changes their email.

Supporting fields on User

For this flow, your user model should probably include:

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    curp = models.CharField(max_length=18, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=False)  # activate after email ownership proven
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

For your spec, is_active=False until magic-link verification is completed is a clean design.

Full flow: signup or login request
Step 1: user submits email

Frontend calls something like:

POST /auth/email/request-link

Payload:

{
  "email": "alex@example.com",
  "intent": "signup"
}

The backend should:

normalize the email

rate limit by IP and email

look up user by email

branch depending on whether user exists

create a magic link token

send email

always return a generic success response

Important anti-enumeration rule

Do not reveal whether an email exists.

Return the same response for both:

{
  "detail": "If the email is valid, a sign-in link has been sent."
}

That prevents attackers from discovering registered emails.

Signup vs login behavior

Because your spec allows email account creation and login, the endpoint can behave like this:

If user does not exist

create a new user with that email

is_active=False

issue a token with purpose signup or email_verify

If user exists

issue a token with purpose login

That means the same email flow can support both account creation and returning-user login.

Example service code
# backend/accounts/services/magic_links.py
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import MagicLinkToken

User = get_user_model()

MAGIC_LINK_TTL_MINUTES = 15


@transaction.atomic
def request_magic_link(*, email: str, intent: str, ip: str | None, user_agent: str) -> None:
    email = email.strip().lower()

    user = User.objects.filter(email=email).first()

    if user is None:
        user = User.objects.create(
            email=email,
            is_active=False,
        )
        purpose = MagicLinkToken.Purpose.SIGNUP
    else:
        purpose = MagicLinkToken.Purpose.LOGIN

    raw_token = MagicLinkToken.generate_raw_token()
    token_hash = MagicLinkToken.hash_token(raw_token)

    record = MagicLinkToken.objects.create(
        user=user,
        email=email,
        token_hash=token_hash,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=MAGIC_LINK_TTL_MINUTES),
        requested_ip=ip,
        user_agent=user_agent[:1000],
    )

    send_magic_link_email(
        email=email,
        raw_token=raw_token,
        token_id=str(record.id),
        purpose=purpose,
    )
What goes in the email link

Use a link like:

https://app.verso.mx/auth/magic/verify?token=<raw_token>&id=<uuid>

Why include both?

id helps find the record quickly

token is the secret

database verifies sha256(token) == token_hash

You can also include a signed next parameter for redirect handling.

Email sending

The email itself should contain:

a button with the magic link

plain text fallback URL

expiry message, like “This link expires in 15 minutes”

security notice, like “If you did not request this, ignore this email”

Do email sending asynchronously through a job queue in production, but the auth request should still immediately persist the token before enqueueing.

Step 2: user clicks the magic link

Frontend usually opens a route like:

GET /auth/magic/verify?...

There are two common patterns:

Pattern A: frontend receives the token, then calls backend

browser lands on frontend page

frontend extracts token and sends it to backend via POST

backend verifies and returns auth success

Pattern B: backend verifies directly

browser hits backend endpoint directly

backend verifies token

backend sets cookie session

backend redirects to app

For web + mobile, I prefer:

Recommended

GET endpoint only receives the link and renders or redirects safely

actual consumption happens in a POST endpoint

That reduces accidental token leakage through logs, browser prefetchers, and link scanners.

Example:

Email link hits:
GET /auth/magic/verify?id=...&token=...

Backend shows an interstitial page or redirects to frontend

Frontend calls:
POST /auth/magic/consume

Token verification logic

When consuming the token:

find token row by id

check it exists

check used_at is null

check expires_at > now

hash provided raw token

compare in constant time

mark token as used

activate user if needed

mark email verified

create session

write audit log

optionally prompt passkey enrollment

Example:

# backend/accounts/services/magic_links.py
import secrets
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

def consume_magic_link(*, token_id: str, raw_token: str, ip: str | None, user_agent: str):
    with transaction.atomic():
        record = (
            MagicLinkToken.objects
            .select_for_update()
            .select_related("user")
            .filter(id=token_id)
            .first()
        )

        if record is None:
            raise ValidationError("Invalid or expired link.")

        if record.is_used or record.is_expired:
            raise ValidationError("Invalid or expired link.")

        presented_hash = MagicLinkToken.hash_token(raw_token)
        if not secrets.compare_digest(presented_hash, record.token_hash):
            raise ValidationError("Invalid or expired link.")

        record.used_at = timezone.now()
        record.save(update_fields=["used_at"])

        user = record.user
        changed_fields = []

        if not user.is_active:
            user.is_active = True
            changed_fields.append("is_active")

        if user.email_verified_at is None:
            user.email_verified_at = timezone.now()
            changed_fields.append("email_verified_at")

        if changed_fields:
            user.save(update_fields=changed_fields)

        create_auth_audit_event(
            user=user,
            event_type="magic_link_login_success",
            ip=ip,
            user_agent=user_agent,
        )

        return user

select_for_update() matters because it prevents race conditions where the same link is consumed twice at the same time.

How login session gets created

In Django session auth:

from django.contrib.auth import login

def finalize_login(request, user):
    login(request, user)
    request.session.set_expiry(3600)  # 1 hour idle timeout

For your spec, you also want an absolute timeout of 24 hours. Django only directly handles idle expiry well, so add your own middleware.

Example approach

Store a session creation timestamp:

request.session["session_started_at"] = timezone.now().isoformat()
request.session.set_expiry(3600)

Then in middleware:

if now - session_started_at > 24 hours, force logout

if idle > 1 hour, session expires naturally

Also rotate the session key on login:

request.session.cycle_key()

That protects against session fixation.

Where to store session state

Because you want device-specific sessions and better operational control:

use Redis-backed Django sessions or database sessions

keep secure, HttpOnly, SameSite=Lax or Strict cookies

always require HTTPS

If you later support mobile native clients, you may prefer a session-token model or short-lived access token plus refresh token pattern, but for normal Django web auth, server-side sessions are fine.

Audit trail design

Your spec explicitly requires every attempt to be logged with timestamp, IP, and device fingerprint.

Add a model like:

class AuthEvent(models.Model):
    EVENT_CHOICES = [
        ("magic_link_requested", "magic_link_requested"),
        ("magic_link_request_denied", "magic_link_request_denied"),
        ("magic_link_login_success", "magic_link_login_success"),
        ("magic_link_login_failure", "magic_link_login_failure"),
        ("google_login_success", "google_login_success"),
        ("passkey_login_success", "passkey_login_success"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(blank=True, default="")
    event_type = models.CharField(max_length=64, choices=EVENT_CHOICES)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    device_fingerprint = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

Log both success and failure. Even if the email does not exist, log the request.

Rate limiting

You need two kinds:

IP-based

Protects against bot spraying from one network.

Identifier-based

Protects against repeated abuse targeting one email.

In Django, good options are:

django-ratelimit

custom Redis counters

proxy or gateway limits at the edge too

Example policy

/auth/email/request-link

5 per 15 minutes per email

20 per hour per IP

/auth/magic/consume

10 failed attempts per hour per IP

maybe 5 failed attempts per token id

If rate-limited, still return a generic response on request-link.

Security concerns that matter a lot
1. Email scanners and link prefetchers

Some email providers or corporate filters open links automatically.

If your magic link is consumed on simple GET, the scanner can accidentally log the user in or invalidate the link.

That is why GET should not consume the token. Use GET only as a handoff, and require POST or a confirmation step to complete login.

2. Single use

Always mark token as used atomically.

3. Short expiry

Use 10 to 15 minutes. Not hours.

4. Revoke older outstanding tokens

When issuing a new login token for the same user and purpose, you may optionally invalidate older unused tokens.

5. Never store raw token

Only store the hash.

6. Constant-time comparison

Use secrets.compare_digest.

7. Do not leak account existence

Same response for registered and unregistered emails.

8. Redirect safety

Never trust arbitrary next URLs. Only allow known internal paths or a whitelist.

9. CSRF and session cookies

If you use cookie-based session login from browser, make the token consumption endpoint CSRF-safe for your frontend architecture.

10. Device and risk handling

Because your spec wants high-risk step-up, you can tag a magic-link login from a new device as lower assurance than passkey and require 2-step verification later for sensitive actions.

How this fits the spec exactly

From your spec:

“Mandatory verification before account activation”

Perfect fit:

create user with is_active=False

after successful magic-link consumption:

set email_verified_at

set is_active=True

“No password login allowed”

That is easy:

custom auth views only

no password set flows

admin access handled separately if needed

“Passkey-first”

After first magic-link login, redirect user into:

dashboard if passkey already exists

passkey enrollment prompt if none exists

So magic link becomes the fallback and bootstrap path.

“One account per unique email”

Enforced with unique=True on user email.

“Session expiration”

Implemented via idle timeout plus absolute session age middleware.

“Audit trail”

Handled with AuthEvent.

Suggested endpoint layout

I would structure it like this:

Request a link

POST /api/v1/auth/email/request-link

Request:

{
  "email": "alex@example.com"
}

Response:

{
  "detail": "If the email is valid, a sign-in link has been sent."
}
Validate preview

GET /api/v1/auth/magic/verify?id=...&token=...

Purpose:

validate shape

maybe store pending token in short-lived signed state

redirect to frontend confirmation page

Consume

POST /api/v1/auth/magic/consume

Request:

{
  "id": "uuid",
  "token": "raw-token"
}

Response:

{
  "authenticated": true,
  "user": {
    "email": "alex@example.com",
    "first_name": null,
    "last_name": null
  },
  "next_step": "enroll_passkey"
}
Logout

POST /api/v1/auth/logout

Session info

GET /api/v1/auth/me

Example Django Rest Framework serializers
from rest_framework import serializers


class RequestMagicLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConsumeMagicLinkSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    token = serializers.CharField(max_length=512)
Example views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .serializers import RequestMagicLinkSerializer, ConsumeMagicLinkSerializer
from .services.magic_links import request_magic_link, consume_magic_link


class RequestMagicLinkView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RequestMagicLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_magic_link(
            email=serializer.validated_data["email"],
            intent="auto",
            ip=get_client_ip(request),
            user_agent=request.headers.get("User-Agent", ""),
        )

        return Response(
            {"detail": "If the email is valid, a sign-in link has been sent."},
            status=status.HTTP_200_OK,
        )


class ConsumeMagicLinkView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ConsumeMagicLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = consume_magic_link(
            token_id=str(serializer.validated_data["id"]),
            raw_token=serializer.validated_data["token"],
            ip=get_client_ip(request),
            user_agent=request.headers.get("User-Agent", ""),
        )

        login(request, user)
        request.session.cycle_key()
        request.session["session_started_at"] = timezone.now().isoformat()
        request.session.set_expiry(3600)

        next_step = "dashboard"
        if not user.webauthn_credentials.exists():
            next_step = "enroll_passkey"

        return Response(
            {
                "authenticated": True,
                "next_step": next_step,
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )
How I would think about “signed URLs” in your open question

Your spec says the decision is “custom Django implementation with signed URLs.”

In Django, that usually means django.core.signing.

You can encode something like:

from django.core import signing

payload = {
    "uid": str(user.id),
    "purpose": "login",
    "nonce": "...",
}
signed_value = signing.dumps(payload, salt="magic-link")

and later:

payload = signing.loads(signed_value, salt="magic-link", max_age=900)

That protects integrity and expiry.

But by itself, it is still weaker operationally because:

harder to revoke individually

harder to mark single-use

harder to audit exactly which link was consumed

harder to defend against replay cleanly

So my recommendation is:

Best practical design

Use database-backed one-time tokens, and optionally sign the URL wrapper as an extra integrity layer.

What happens across devices

Magic link works well cross-device:

user requests link on desktop

opens email on phone

taps link

either logs in on phone, or

if you support it, show a confirmation/handoff flow back to original device

For MVP, simplest is:

the device that clicks the link becomes the logged-in device

That is normal behavior for magic links.

What tests you should absolutely write

For T2, I would include at least these:

Request flow

request link for new email creates inactive user

request link for existing email does not create second user

response does not reveal whether email exists

token row is created

email task is queued or sent

Consume flow

valid token logs user in

token becomes used after success

used token cannot be reused

expired token fails

wrong token fails

wrong token id fails

successful signup token activates user

successful login token preserves active user

Security

rate limit triggers correctly

older token invalidation behavior works if implemented

audit event created on success

audit event created on failure

session expiry metadata set

redirect whitelist enforced

Concurrency

two simultaneous consume attempts only allow one success

That last one is important and often missed.

Minimal implementation summary

At a high level, the backend algorithm is:

Request phase

normalize email

rate limit

find or create user

create one-time token record

hash token and store hash

send raw token in email link

log audit event

Consume phase

receive token id + token

lock token row

check unused and unexpired

compare hashed token

mark used

verify email and activate account

create authenticated session

log audit event

prompt passkey enrollment

My recommendation for this project

Given your product priorities, I would implement email magic links in Django as:

custom user model

database-backed MagicLinkToken table

hashed random tokens

single-use + 15 minute expiry

generic responses to avoid enumeration

audit event table

Redis-backed rate limiting

GET does not consume token

POST consumes token atomically

session cookie auth for web

prompt passkey registration immediately after first successful magic-link login

That matches the spec well and is much safer than a purely stateless signed-link approach.
