# Fundraiser model

Not By Chance Outreach — winter shelter equipment.

This document separates **what the money is for** from **how a Chia NFT happens to move money**. Those are easy to conflate. They are not the same.

## 1. Direct supply target (the goods)

| Item | Count | Unit cost | Line total |
| --- | ---: | ---: | ---: |
| 3-person tents | 200 | $15 | $3,000 |
| 6-person tents | 200 | $30 | $6,000 |
| Sleeping bags | 400 | $7.50 | $3,000 |
| **Goods subtotal** | **800** |  | **$12,000** |

The NFT supply matches this table on purpose: 200 Pups, 200 Lodges, 400 Snugs.

## 2. Contingency (not a royalty)

The brief includes an additional **10% economic component** intended to cover unexpected costs of completing the order: substitutions, tax, shipping, damaged goods, last-minute price changes, platform friction.

| | Amount |
| --- | ---: |
| Goods | $12,000 |
| 10% contingency | $1,200 |
| **Gross campaign target** | **$13,200** |

**This 10% is not a secondary-sale NFT royalty.**

It is a budgeted overrun allowance on the **primary** raise.

Two different knobs, named clearly:

| Knob | When it happens | What it is | Status |
| --- | --- | --- | --- |
| **A. Primary mint contingency** | At mint, in the price the buyer pays | Extra $1,200 across 800 tokens to finish the order | Recommended default. This is the 10% in the brief. |
| **B. Secondary-market creator royalty** | Later, if a token is resold | A Chia NFT1 royalty / transfer-program percentage on secondary sales | **Not decided.** Separate Chia implementation. Do not describe knob A as knob B. |

If a secondary royalty is later enabled, say so in its own sentence: "A royalty on resales, if any, is a distinct on-chain setting and is not the 10% contingency built into the mint target."

## 3. A clean way to price the mint in USD terms

If the 10% rides along in the primary price, class mint targets can follow the physical items:

| NFT class | Physical unit | Unit + 10% | Count | Class total |
| --- | ---: | ---: | ---: | ---: |
| Snug | $7.50 | **$8.25** | 400 | $3,300 |
| Pup | $15.00 | **$16.50** | 200 | $3,300 |
| Lodge | $30.00 | **$33.00** | 200 | $6,600 |
| **Total** |  |  | **800** | **$13,200** |

This is optional. A flat $16.50 mint also sums to $13,200 and is simpler to explain; it decouples token price from item cost. Both are honest if the copy is honest.

**Recommendation:** class-priced mint, because it teaches the 1:1 story. Final call is the organization's.

## 4. What mint price is *not*

- Not an XCH number. XCH/USD moves. Conversion policy is a later operations doc (snapshot FX, extra buffer, or priced-in-USD-settled-in-XCH).
- Not a guarantee that marketplace fees, on-chain mint fees, or payment-processor fees are already inside the $13,200. Call those out separately when the Chia path is chosen. If they come *out of* the $13,200, either raise the mint or accept a smaller goods purchase. Do not pretend the chain is free.
- Not a claim that buying Lodge #0612 legally assigns the buyer a particular six-person tent in a warehouse.

## 5. Language for listings and metadata

Use:

> This NFT is one of 200 Lodges. The campaign's goal is to purchase 200 six-person tents. Ownership of this NFT does not convey legal title to a specific physical tent.

Do not use:

> This NFT *is* tent #0612.
> You own the physical tent.
> 10% royalties go to charity.

If a buyer wants a physical item, that is a different product (a print, a thank-you, a named dedication) and must be specified as such.

## 6. Open decisions (not silently filled in)

- USD vs XCH pricing and who eats FX.
- Whether class-priced or flat mint.
- Whether any **secondary** royalty exists, at what percent, and to which address / DID.
- How leftover contingency is reported if the order comes in under $12,000 (buy more gear vs. hold vs. next season).
- How a shortfall is handled if the collection does not sell out.

Phase 0 only needs the distinction between A and B, and the $12,000 / $13,200 arithmetic, to be unambiguous in public copy.
