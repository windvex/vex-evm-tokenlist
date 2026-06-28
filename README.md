# VEX EVM Token List

Official token list for VEX EVM (Chain ID: 6736). Compatible with Uniswap token list standard.

**Token List URL:**
```
https://raw.githubusercontent.com/pixelgenius-id/vex-evm-tokenlist/main/tokenlist.json
```

---

## How to Submit Your Token

### Step 1 — Fork this repo

Click the **Fork** button at the top right of this page, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/vex-evm-tokenlist.git
cd vex-evm-tokenlist
```

### Step 2 — Prepare your logo

- Format: **PNG**
- Size: exactly **256×256 px**
- Max file size: **50 KB**
- Filename: your token contract address in **all lowercase** + `.png`

Example: if your contract is `0xAbCd...1234`, the file must be named:
```
0xabcd...1234.png
```

Place the file in the `assets/` folder:
```
assets/
  0xabcd...1234.png
```

### Step 3 — Add your token to `tokenlist.json`

Add a new entry inside the `"tokens"` array:

```json
{
  "chainId": 6736,
  "address": "0xabcd...1234",
  "name": "Your Token Full Name",
  "symbol": "SYM",
  "decimals": 18
}
```

> **Do not add `logoURI`** — it will be set automatically after your PR is merged.
> If you include `logoURI`, the validation will fail.

> The `address` must be **all lowercase**.

### Step 4 — Submit a Pull Request

Push your changes and open a PR against the `main` branch of this repo. GitHub Actions will automatically run validation checks and post the result as a comment on your PR.

---

## Listing Requirements

| Requirement | Detail |
|-------------|--------|
| Chain | VEX EVM, chainId **6736** |
| Contract | Must be deployed on VEX EVM |
| Contract age | Minimum **7 days** since deployment |
| Liquidity | Minimum **500 VEX** in a SPARK Swap pool |
| Logo file | PNG, exactly **256×256 px**, max **50 KB** |
| Logo filename | `assets/<lowercase_address>.png` |
| No honeypot | Buy and sell must work freely |

---

## Automated Validation

When you open a PR, GitHub Actions automatically checks:

- JSON is valid and all required fields are present
- `chainId` is 6736
- Contract is deployed on VEX EVM (`eth_getCode` returns bytecode)
- Contract was deployed at least 7 days ago
- Liquidity ≥ 500 VEX in a registered swap pool
- Logo exists at `assets/<address>.png`, is exactly 256×256 px, PNG format, and ≤ 50 KB
- No existing tokens were removed from the list

All checks must pass before a maintainer will review your PR.

---

## After Merge

Once your PR is merged, your token will automatically appear in:
- **SPARK Swap** token selector
- **VEXascan** EVM token list

No additional steps needed.

---

## Updating Your Logo

To replace your token's logo, submit a new PR with just the updated logo file:

1. Fork and clone the repo
2. Replace `assets/0xaddress.png` with your new logo (same filename, same 256×256 PNG requirements)
3. Do **not** modify `logoURI` in `tokenlist.json` — it will be updated automatically after merge
4. Submit a Pull Request

---

## Resources

- [SPARK Swap](https://swap.nodespark.fun)
- [VEXascan Explorer](https://vexascan.com)
- [VEX EVM Info](https://vexascan.com/evm)
