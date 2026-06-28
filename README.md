# VEX EVM Token List

Official token list for VEX EVM (Chain ID: 6736). Compatible with Uniswap token list standard.

**Token List URL:**
```
https://raw.githubusercontent.com/YudaAdiPratama/vex-evm-tokenlist/main/tokenlist.json
```

## Submit a Token

1. Fork this repo
2. Add your token to `tokenlist.json`
3. Add logo to `assets/<checksum_address>.png`
4. Submit a Pull Request

## Listing Requirements

| Requirement | Detail |
|-------------|--------|
| Chain | VEX EVM (chainId: 6736) |
| Contract | Must be deployed and verified |
| Contract age | Minimum **7 days** since deployment |
| Liquidity | Minimum **500 VEX** in SPARK Swap pool |
| Logo | **256×256px PNG**, max **50KB**, named `<address>.png` |
| Not a honeypot | Buy and sell must work freely |

## tokenlist.json Entry Format

```json
{
  "chainId": 6736,
  "address": "0xYourTokenAddress",
  "name": "Token Full Name",
  "symbol": "SYM",
  "decimals": 18,
  "logoURI": "https://raw.githubusercontent.com/YudaAdiPratama/vex-evm-tokenlist/main/assets/0xyourtokenaddress.png"
}
```

> **Note:** Address in `logoURI` must be **lowercase checksum** (all lowercase).

## PR Review Process

1. GitHub Actions runs automated checks on every PR
2. All automated checks must pass (green)
3. Maintainer does manual review (honeypot check, social presence)
4. If approved → merged → token appears in SPARK Swap

## Resources

- [SPARK Swap](https://swap.nodespark.fun)
- [VEX Explorer](https://vexascan.com)
- [VEX EVM RPC](https://vexascan.com/evm)
