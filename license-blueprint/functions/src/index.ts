import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { createHash } from "crypto";

admin.initializeApp();

const db = admin.firestore();

interface License {
    key_id: string;
    hash: string;
    assigned_to: string | null;
    assigned_at: admin.firestore.Timestamp | null;
    revoked: boolean;
}

interface BusinessLimits {
    reservations_month: number | null;
    branches: number | null;
    staff: number | null;
    sms: number | null;
}

interface Business {
    plan: "free" | "starter" | "pro" | "license";
    limits: BusinessLimits;
}

/**
 * SHA-256 Utility
 */
function sha256(text: string): string {
    return createHash("sha256").update(text).digest("base64");
}

/**
 * Callable function to activate a license key for a business.
 */
export const activateLicense = functions.https.onCall(async (data: { key: string; business_id: string }, context: functions.https.CallableContext) => {
    // 1. Auth Require Owner/Admin (Simplified for blueprint, assuming business_id check)
    if (!context.auth) {
        throw new functions.https.HttpsError(
            "unauthenticated",
            "User must be authenticated."
        );
    }

    const { key, business_id } = data;

    if (!key || !business_id) {
        throw new functions.https.HttpsError(
            "invalid-argument",
            "Key and business_id are required."
        );
    }

    const hashed = sha256(key);

    return db.runTransaction(async (transaction: admin.firestore.Transaction) => {
        // 2. Fetch license with hash
        const licenseRef = db.collection("licenses").where("hash", "==", hashed).where("revoked", "==", false).limit(1);
        const licenseSnap = await transaction.get(licenseRef);

        if (licenseSnap.empty) {
            throw new functions.https.HttpsError("not-found", "Invalid or revoked license key.");
        }

        const licDoc = licenseSnap.docs[0];
        const licData = licDoc.data() as License;

        // 3. Validation: already used
        if (licData.assigned_to && licData.assigned_to !== business_id) {
            throw new functions.https.HttpsError("already-exists", "License key already assigned to another business.");
        }

        if (licData.assigned_to === business_id) {
            return { plan: "license", status: "already_active" };
        }

        // 4. Tx Assert count < 5 for this specific business
        const activeLicensesRef = db.collection("licenses")
            .where("assigned_to", "==", business_id)
            .where("revoked", "==", false);
        const activeLicensesSnap = await transaction.get(activeLicensesRef);

        if (activeLicensesSnap.size >= 5) {
            throw new functions.https.HttpsError("resource-exhausted", "Maximum limit of 5 active licenses reached for this business.");
        }

        // 5. Update License
        transaction.update(licDoc.ref, {
            assigned_to: business_id,
            assigned_at: admin.firestore.FieldValue.serverTimestamp(),
        });

        // 6. Update Business
        const businessRef = db.collection("businesses").doc(business_id);
        const unlimitedLimits: BusinessLimits = {
            reservations_month: null,
            branches: null,
            staff: null,
            sms: null,
        };

        transaction.update(businessRef, {
            plan: "license",
            limits: unlimitedLimits,
        });

        return { plan: "license", limits: unlimitedLimits };
    });
});
