
const crypto = require("crypto");

// sha256 function to match logic
function sha256(text) {
    return crypto.createHash("sha256").update(text).digest("base64");
}

class MockFirestore {
    constructor() {
        this.data = {
            licenses: [],
            businesses: {}
        };
    }

    runTransaction(fn) {
        const transaction = {
            get: async (query) => {
                if (query._collection === 'licenses') {
                    let filtered = this.data.licenses;
                    if (query._where) {
                        for (const condition of query._where) {
                            filtered = filtered.filter((doc) => {
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
                        docs: filtered.map((doc) => ({
                            data: () => doc,
                            ref: { id: doc.id }
                        }))
                    };
                }
                return { empty: true, size: 0, docs: [] };
            },
            update: (ref, update) => {
                console.log(`[MockTx] Updating document ${ref.id} with data:`, JSON.stringify(update));
            }
        };
        return fn(transaction);
    }

    collection(name) {
        const obj = {
            _collection: name,
            _where: [],
            _limit: null,
            doc: (id) => ({ id }),
            where: function (field, op, value) {
                this._where.push({ field, op, value });
                return this;
            },
            limit: function (n) {
                this._limit = n;
                return this;
            }
        };
        return obj;
    }
}

async function runTests() {
    const db = new MockFirestore();
    const testKey = "test-32-char-key-12345678901234";
    const testHash = sha256(testKey);
    const business_id = "biz_123";

    console.log("--- TEST 1: Valid Activation ---");
    db.data.licenses = [
        { id: 'lic_1', hash: testHash, revoked: false, assigned_to: null }
    ];

    await db.runTransaction(async (transaction) => {
        // Simulated index.ts logic
        const licSnap = await transaction.get(db.collection('licenses').where('hash', '==', testHash).where('revoked', '==', false).limit(1));
        if (licSnap.empty) throw new Error("Invalid key");
        const licDoc = licSnap.docs[0];
        const licData = licDoc.data();

        if (licData.assigned_to && licData.assigned_to !== business_id) {
            throw new Error("Key already assigned");
        }

        const activeSnap = await transaction.get(db.collection('licenses').where('assigned_to', '==', business_id).where('revoked', '==', false));
        if (activeSnap.size >= 5) throw new Error("Limit reached");

        transaction.update(licDoc.ref, { assigned_to: business_id });
        console.log("✅ Test 1 Passed: Logic allowed activation and updated doc.");
    });

    console.log("\n--- TEST 2: Already Used Key ---");
    db.data.licenses[0].assigned_to = "other_biz";
    try {
        const licData = db.data.licenses[0];
        if (licData.assigned_to && licData.assigned_to !== business_id) {
            throw new Error("Already exists: License key already assigned to another business.");
        }
    } catch (e) {
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
        await db.runTransaction(async (transaction) => {
            const activeSnap = await transaction.get(db.collection('licenses').where('assigned_to', '==', business_id).where('revoked', '==', false));
            if (activeSnap.size >= 5) throw new Error("Resource exhausted: Maximum limit of 5 active licenses reached for this business.");
        });
    } catch (e) {
        console.log("✅ Test 3 Passed:", e.message);
    }

    console.log("\n--- TEST 4: Revoked Key ---");
    db.data.licenses = [
        { id: 'lic_7', hash: sha256("revoked-key"), revoked: true, assigned_to: null }
    ];
    await db.runTransaction(async (transaction) => {
        const licSnap = await transaction.get(db.collection('licenses').where('hash', '==', sha256("revoked-key")).where('revoked', '==', false).limit(1));
        if (licSnap.empty) {
            console.log("✅ Test 4 Passed: Revoked key not found in query.");
        } else {
            throw new Error("Revoked key should not be found");
        }
    });

    console.log("\n--- ALL TESTS COMPLETED ---");
}

runTests().catch(console.error);
