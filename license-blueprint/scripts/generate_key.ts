import { createHash, randomBytes } from "crypto";

function sha256(text: string): string {
    return createHash("sha256").update(text).digest("base64");
}

function generateKey(length: number = 32): string {
    return randomBytes(length).toString("hex").slice(0, length);
}

const key = generateKey();
const hash = sha256(key);

console.log("=== Universal License Key Discovery ===");
console.log(`Key (Distribute to Client): ${key}`);
console.log(`Hash (Insert into Firestore): ${hash}`);
console.log("========================================");
console.log("\nFirestore Document Data:");
console.log(JSON.stringify({
    key_id: key.substring(0, 8),
    hash: hash,
    assigned_to: null,
    assigned_at: null,
    revoked: false
}, null, 2));
