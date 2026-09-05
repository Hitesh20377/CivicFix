# CivicFix Security Audit & Fixes Implementation Plan

This document outlines the proposed fixes and tests for the 21-point CivicFix security audit.

## User Review Required
> [!IMPORTANT]
> - MinIO is not actively integrated for file attachment storage. Attachments are currently stored locally in `instance/uploads/`.
> - A new API endpoint will be added to securely serve downloaded attachments with appropriate authorization checks. 

## Open Questions
> [!NOTE]
> Are there any specific export endpoints currently active that I missed? (I found `ReportingService` but no explicit route exposing it). If there is an `api.py` serving these, I will secure them there.

## Proposed Changes

### Role-Based Authorization
- **Fix**: The `require_role` decorator currently throws an `AttributeError` when passed a list. I will fix the decorator in `roles.py` to properly handle `*allowed_roles` tuples/lists and correctly check `user.role.name` versus string values.

### Logout and Token Revocation
- **Fix**: Make sure `auth_middleware.py` robustly checks the blocklist. While it currently fails open if Redis is down (to prevent locking out users), I will add logging and secure it properly.

### Private Attachment Access
- **Fix**: Create a secure endpoint `GET /api/issues/<issue_id>/attachments/<attachment_id>` in `issues.py` that verifies the user has authorization to view the issue before serving the file with `send_from_directory(secure_filename)`.

### Unauthorized Export Reports
- **Fix**: Ensure any analytics or export routes (like those using `ReportingService` inside `backend/app/api.py`) apply `@require_role('ADMIN', 'MUNICIPAL_OFFICER')` to prevent citizen access to system-wide data exports.

### API Error Stack Traces
- **Fix**: Validate that `handle_generic_exception` in `errors/handlers.py` sets `exc_info=False` in production or does not leak it to the JSON response payload.

### File Validation (Type & Size & Path Traversal)
- **Fix**: Ensure `secure_filename()` is always used for both saving and retrieving files. The 5MB size limit is already enforced by Flask, but I will write a test for it.

### Tests
- Create `backend/tests/test_security.py` to add real tests for every security check explicitly verifying these conditions using pytest.

## Verification Plan

### Automated Tests
Run the security test suite against the backend:
`pytest backend/tests/test_security.py -v`

### Manual Verification
- Will verify no stack traces are leaked on intentional 500s.
- Will verify attachments cannot be downloaded via path traversal.
- Will verify roles properly restrict access and `require_role` works correctly.
