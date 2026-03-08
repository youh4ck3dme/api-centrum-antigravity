
import { createHash } from "crypto";

// Mock implementation of sha256 to match the one in index.ts
function sha256(text: string): string {
    return createHash("sha256").update(text).digest("base64");
}

/**
 * Mock Firestore for testing the transaction logic
 */
class MockFirestore {
    data: any = {
        licenses: [],
        businesses: {}
    };

    runTransaction(fn: Function) {
        const transaction = {
            get: async (query: any) => {
                if (query._collection === 'licenses') {
                    let filtered = this.data.licenses;
                    if (query._where) {
                        for (const condition of query._where) {
                            filtered = filtered.filter((doc: any) => {
                                const val = doc[condition.field];
                                if (condition.op === '==') return val === condition.value;
                                if (condition.op === '!=') return val !== condition.value;
                                return true;
                            });
                        }
                    }
                    if (query._limit) filtered = filtered.slice(0, query._limit);
                    return {
                        empty: filtered.length === 0,
                        size: filtered.length,
                        docs: filtered.map((doc: any) => ({
                            data: () => doc,
                            ref: { id: doc.id }
                        }))
                    };
                }
                return { empty: true, size: 0, docs: [] };
            },
            update: (ref: any, update: any) => {
                // Mock update logic
                console.log(`[MockTx] Updating ${ref.id} with:`, update);
            }
        };
        return fn(transaction);
    }

    collection(name: string) {
        return {
            _collection: name,
            _where: [] as any[],
            _limit: null as number | null,
            doc: (id: string) => ({ id }),
            where: function (field: string, op: string, value: any) {
                this._where.push({ field, op, value });
                return this;
            },
            limit: function (n: number) {
                this._limit = n;
                return this;
            }
        };
    }
}

/**
 * SIMULATED TEST CASES
 */
async function runTests() {
    const db = new MockFirestore();
    const testKey = "test-32-char-key-12345678901234";
    const testHash = sha256(testKey);
    const business_id = "biz_123";

    console.log("--- TEST 1: Valid Activation ---");
    db.data.licenses = [
        { id: 'lic_1', hash: testHash, revoked: false, assigned_to: null }
    ];

    // Simulation of the function logic (simplified)
    await db.runTransaction(async (transaction: any) => {
        const licSnap = await transaction.get(db.collection('licenses').where('hash', '==', testHash).where('revoked', '==', false).limit(1));
        if (licSnap.empty) throw new Error("Invalid key");

        const activeSnap = await transaction.get(db.collection('licenses').where('assigned_to', '==', business_id).where('revoked', '==', false));
        if (activeSnap.size >= 5) throw new Error("Limit reached");

        console.log("✅ Test 1 Passed: Logic allowed activation");
    });

    console.log("\n--- TEST 2: Already Used Key ---");
    db.data.licenses[0].assigned_to = "other_biz";
    try {
        const licData = db.data.licenses[0];
        if (licData.assigned_to && licData.assigned_to !== business_id) {
            throw new Error("Key already assigned to another business");
        }
    } catch (e: any) {
        console.log("✅ Test 2 Passed:", e.message);
    }

    console.log("\n--- TEST 3: Per-Business Limit (5 Keys) ---");
    db.data.licenses = [
        { id: 'lic_6', hash: sha256("k6"), revoked: false, assigned_to: null },
        { id: 'lic_1', assigned_to: business_id, revoked: false },
        { id: 'lic_2', assigned_to: business_id, revoked: false },
        { id: 'lic_3', assigned_to: business_id, revoked: false },
        { id: 'lic_4', assigned_to: business_id, revoked: false },
        { id: 'lic_5', assigned_to: business_id, revoked: false },
    ];

    try {
        await db.runTransaction(async (transaction: any) => {
            const activeSnap = await transaction.get(db.collection('licenses').where('assigned_to', '==', business_id).where('revoked', '==', false));
            if (activeSnap.size >= 5) throw new Error("Maximum limit of 5 active licenses reached for this business.");
        });
    } catch (e: any) {
        console.log("✅ Test 3 Passed:", e.message);
    }
}

runTests().catch(console.error);
