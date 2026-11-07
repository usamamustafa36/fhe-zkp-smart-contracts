#!/bin/bash
#
# Soundness regression test for range_commit.circom
# =================================================
#
# Checks that the witness generator accepts in-range values and rejects
# out-of-range ones, including the field-wraparound value x = p - 1
# ("-1" in the BN254 scalar field). Before the Num2Bits(32) constraint was
# added, x = p - 1 produced a valid Groth16 proof.
#
# USAGE (from the repository root, after npm install in zkp_prod/):
#   bash zkp_prod/tests/circuit/test_range_soundness.sh
#
set -u
cd "$(dirname "$0")/../../.."
LIB=zkp_prod/node_modules
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

P=21888242871839275222246405745257275088548364400416034343698204186575808495617

# Helper circuit that outputs Poseidon(x, salt, contextHash), used to build
# a commitment that matches each test value.
cat > "$TMP/hash3.circom" <<'EOF'
pragma circom 2.1.6;
include "circomlib/circuits/poseidon.circom";
template H() {
    signal input a; signal input b; signal input c; signal output o;
    component h = Poseidon(3);
    h.inputs[0] <== a; h.inputs[1] <== b; h.inputs[2] <== c;
    o <== h.out;
}
component main = H();
EOF

circom "$TMP/hash3.circom" --wasm -l "$LIB" -o "$TMP" > /dev/null || exit 1
circom zkp_prod/circuits/range_commit.circom --wasm -l "$LIB" -o "$TMP" > /dev/null || exit 1

FAIL=0
check() {  # check <x> <expected: accept|reject> <label>
    local X=$1 WANT=$2 LABEL=$3 C GOT
    echo "{\"a\":\"$X\",\"b\":\"7\",\"c\":\"999\"}" > "$TMP/h.json"
    node "$TMP/hash3_js/generate_witness.js" "$TMP/hash3_js/hash3.wasm" "$TMP/h.json" "$TMP/h.wtns" || exit 1
    snarkjs wtns export json "$TMP/h.wtns" "$TMP/h_w.json" > /dev/null || exit 1
    C=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))[1])" "$TMP/h_w.json")
    echo "{\"x\":\"$X\",\"salt\":\"7\",\"commitment\":\"$C\",\"contextHash\":\"999\"}" > "$TMP/in.json"
    if node "$TMP/range_commit_js/generate_witness.js" "$TMP/range_commit_js/range_commit.wasm" \
            "$TMP/in.json" "$TMP/w.wtns" > /dev/null 2>&1; then GOT=accept; else GOT=reject; fi
    if [ "$GOT" = "$WANT" ]; then echo "   ✅ $LABEL: $GOT"; else echo "   ❌ $LABEL: $GOT (expected $WANT)"; FAIL=1; fi
}

check 0         accept "x = 0"
check 1000000   accept "x = 1,000,000"
check 1000001   reject "x = 1,000,001"
check 4294967296 reject "x = 2^32"
check "$(python3 -c "print($P - 1)")" reject "x = p - 1 (field wraparound)"

exit $FAIL
