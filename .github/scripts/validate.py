#!/usr/bin/env python3
"""
VEX EVM Token List Validator
Runs on every PR that touches tokenlist.json or assets/
"""

import json
import os
import sys
import time
import requests
from PIL import Image

VEX_EVM_RPC   = "https://vexascan.com/evm"
SWAP_API      = "https://vexascan.com/api/v1/swap"
CHAIN_ID      = 6736
MIN_LIQUIDITY = 500   # minimum VEX in pool
MIN_AGE_DAYS  = 7
MAX_LOGO_KB   = 50
LOGO_SIZE     = 256

results = []
failed  = False

def ok(msg):   results.append(f"✅ {msg}")
def fail(msg):
    global failed
    failed = True
    results.append(f"❌ {msg}")
def warn(msg): results.append(f"⚠️ {msg}")
def info(msg): results.append(f"ℹ️ {msg}")

# ── 0. Load base branch tokenlist (detect removed tokens) ─────────────────────
import subprocess

def load_base_tokenlist():
    try:
        out = subprocess.check_output(
            ["git", "show", "origin/main:tokenlist.json"],
            stderr=subprocess.DEVNULL
        )
        return json.loads(out)
    except Exception:
        return None

base_data = load_base_tokenlist()
base_addresses = set()
if base_data:
    base_addresses = {t["address"].lower() for t in base_data.get("tokens", [])}

# ── 1. Parse tokenlist.json ────────────────────────────────────────────────────
try:
    with open("tokenlist.json") as f:
        data = json.load(f)
    ok("tokenlist.json is valid JSON")
except Exception as e:
    fail(f"tokenlist.json parse error: {e}")
    sys.exit(write_result())

required_root = {"name", "version", "tokens"}
if not required_root.issubset(data):
    fail(f"Missing root fields: {required_root - set(data)}")
else:
    ok("Root fields present (name, version, tokens)")

tokens = data.get("tokens", [])
info(f"Total tokens in list: {len(tokens)}")

# ── 1b. Removal guard ─────────────────────────────────────────────────────────
results.append("\n### Removal Guard")
if base_addresses:
    pr_addresses = {t.get("address", "").lower() for t in tokens}
    removed = base_addresses - pr_addresses
    if removed:
        for addr in sorted(removed):
            fail(f"Token `{addr}` was removed — existing tokens cannot be delisted via PR")
    else:
        ok(f"No existing tokens removed ({len(base_addresses)} checked)")
else:
    warn("Could not load base branch — skipping removal check")

# ── 2. Per-token validation ────────────────────────────────────────────────────
REQUIRED_FIELDS = {"chainId", "address", "name", "symbol", "decimals", "logoURI"}

def rpc(method, params):
    r = requests.post(VEX_EVM_RPC, json={
        "jsonrpc": "2.0", "id": 1,
        "method": method, "params": params
    }, timeout=10)
    return r.json().get("result")

for token in tokens:
    addr   = token.get("address", "").lower()
    symbol = token.get("symbol", "?")
    name   = token.get("name", "?")
    label  = f"`{symbol}` ({addr[:10]}...)"

    results.append(f"\n### {symbol} — {name}")

    # Required fields
    missing = REQUIRED_FIELDS - set(token)
    if missing:
        fail(f"{label}: Missing fields: {missing}")
        continue
    ok(f"{label}: All required fields present")

    # chainId
    if token["chainId"] != CHAIN_ID:
        fail(f"{label}: chainId must be {CHAIN_ID}, got {token['chainId']}")
    else:
        ok(f"{label}: chainId = {CHAIN_ID}")

    # Address format
    if not addr.startswith("0x") or len(addr) != 42:
        fail(f"{label}: Invalid address format")
    else:
        ok(f"{label}: Address format valid")

    # Contract exists on-chain
    try:
        code = rpc("eth_getCode", [addr, "latest"])
        if not code or code == "0x" or code == "0x0":
            fail(f"{label}: No contract code at address — not deployed on VEX EVM")
        else:
            ok(f"{label}: Contract code found on VEX EVM")
    except Exception as e:
        warn(f"{label}: Could not verify contract on-chain: {e}")

    # Contract age via deploy block
    try:
        # Get earliest tx involving this address
        resp = requests.get(
            f"{SWAP_API.replace('/swap', '')}/evm/token/{addr}",
            timeout=10
        ).json()
        deploy_block = resp.get("deploy_block", 0)
        if deploy_block:
            # Estimate block time: VEX EVM ~0.5s per block
            age_seconds = deploy_block * 0.5  # rough
            # Better: get current block
            cur_block_hex = rpc("eth_blockNumber", [])
            cur_block = int(cur_block_hex, 16) if cur_block_hex else 0
            age_blocks = cur_block - deploy_block
            age_days = (age_blocks * 0.5) / 86400
            if age_days < MIN_AGE_DAYS:
                fail(f"{label}: Contract age {age_days:.1f}d < {MIN_AGE_DAYS}d minimum")
            else:
                ok(f"{label}: Contract age {age_days:.1f}d ≥ {MIN_AGE_DAYS}d")
    except Exception as e:
        warn(f"{label}: Could not check contract age: {e}")

    # Liquidity check via swap API
    try:
        pairs = requests.get(f"{SWAP_API}/pairs", timeout=10).json()
        token_pairs = [
            p for p in pairs.get("pairs", [])
            if addr in (p.get("token0","").lower(), p.get("token1","").lower())
        ]
        if not token_pairs:
            fail(f"{label}: No liquidity pool found on SPARK Swap")
        else:
            # Check max reserve in VEX terms (token paired with WVEX)
            wvex = "0x7b798419f963a253bd3e83d7ed8ca33090c3b890"
            total_vex = 0
            for p in token_pairs:
                if wvex in (p.get("token0","").lower(), p.get("token1","").lower()):
                    r0 = int(p.get("reserve0", 0) or 0)
                    r1 = int(p.get("reserve1", 0) or 0)
                    # whichever side is WVEX
                    vex_res = r1 if p.get("token0","").lower() == wvex else r0
                    total_vex += vex_res / 1e18
            if total_vex < MIN_LIQUIDITY:
                fail(f"{label}: Liquidity {total_vex:.1f} VEX < {MIN_LIQUIDITY} VEX minimum")
            else:
                ok(f"{label}: Liquidity {total_vex:.1f} VEX ≥ {MIN_LIQUIDITY} VEX")
    except Exception as e:
        warn(f"{label}: Could not check liquidity: {e}")

    # Logo: must exist in assets/ directory
    logo_path = f"assets/{addr}.png"
    if not os.path.exists(logo_path):
        fail(f"{label}: Logo not found at {logo_path}")
    else:
        # Size check
        size_kb = os.path.getsize(logo_path) / 1024
        if size_kb > MAX_LOGO_KB:
            fail(f"{label}: Logo {size_kb:.1f}KB > {MAX_LOGO_KB}KB limit")
        else:
            ok(f"{label}: Logo size {size_kb:.1f}KB ≤ {MAX_LOGO_KB}KB")

        # Dimension check
        try:
            img = Image.open(logo_path)
            w, h = img.size
            if w != LOGO_SIZE or h != LOGO_SIZE:
                fail(f"{label}: Logo must be {LOGO_SIZE}×{LOGO_SIZE}px, got {w}×{h}px")
            else:
                ok(f"{label}: Logo dimensions {w}×{h}px ✓")
            if img.format != "PNG":
                fail(f"{label}: Logo must be PNG format, got {img.format}")
            else:
                ok(f"{label}: Logo format PNG ✓")
        except Exception as e:
            fail(f"{label}: Cannot read logo image: {e}")

    # logoURI must match expected pattern
    expected_uri = f"https://raw.githubusercontent.com/pixelgenius-id/vex-evm-tokenlist/main/assets/{addr}.png"
    if token["logoURI"] != expected_uri:
        warn(f"{label}: logoURI should be:\n  `{expected_uri}`")
    else:
        ok(f"{label}: logoURI format correct")

# ── 3. Write result ────────────────────────────────────────────────────────────
def write_result():
    summary = "### ✅ All checks passed — ready for review" if not failed else \
              "### ❌ Validation failed — please fix the issues above"
    output = "\n".join(results) + f"\n\n---\n{summary}"
    print(output)
    with open("/tmp/validation_result.txt", "w") as f:
        f.write(output)
    return 1 if failed else 0

sys.exit(write_result())
