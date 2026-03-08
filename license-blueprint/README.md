# Universal License System Blueprint

This blueprint provides a secure, server-side validated license key system to unlock "unlimited" features for specific business entities.

## Features
- **Max 5 Licenses**: Hard limit of 5 keys per business. Uses Firestore transactions to ensure that the limit of 5 active licenses per business is never exceeded.
- **Hashed Storage**: Keys are never stored in plain text (SHA-256).
- **Server-Side Validation**: Activation logic runs strictly in Firebase Cloud Functions.
- **Universal**: Decoupled from any specific project structure.

## Structure
- `functions/src/index.ts`: The `activateLicense` Cloud Function.
- `firestore.rules`: Security rules to prevent unauthorized plan changes.
- `scripts/generate_key.ts`: Offline utility to generate new keys and hashes.
- `frontend/LicenseActivation.vue`: Ready-to-use Vue 3 component.

## Integration Steps

### 1. Backend (Cloud Functions)
Copy the `activateLicense` function into your Firebase project. Ensure you have `firebase-admin` and `firebase-functions` installed.

### 2. Database (Firestore)
- Create a collection named `licenses`.
- Use the `generate_key.ts` script to generate a key/hash pair.
- Manually add the document to the `licenses` collection:
  ```json
  {
    "key_id": "short-slug",
    "hash": "BASE64_SHA256_HASH",
    "assigned_to": null,
    "assigned_at": null,
    "revoked": false
  }
  ```

### 3. Business Guard (Limit Checks)
In your backend logic (or where you check limits), update your guard to ignore limits if the plan is `license`:

```typescript
// Example usage in other functions
const businessSnap = await db.collection('businesses').doc(id).get();
const business = businessSnap.data();

if (business.plan === 'license') {
  // UNLIMITED - skip limit checks
  return true;
}

// Otherwise, check limits...
if (currentCount >= business.limits.reservations_month) {
  throw new Error("Limit reached");
}
```

### 4. Frontend
Import and use the `LicenseActivation.vue` component in your admin settings panel:

```vue
<LicenseActivation 
  :business-id="currentBusinessId" 
  :business-data="currentBusinessData"
  @activated="refreshData"
/>
```

## Security Design
- The `licenses` collection is restricted so clients cannot write to it.
- The `businesses/{id}/plan` field is protected via rules to only allow writes if the field isn't being modified (effectively making it backend-only for changes).
- Re-activation of the same key for the same business is idempotent.
- Revocation: Set `revoked: true` and `assigned_to: null` on the license document to invalidate it.
