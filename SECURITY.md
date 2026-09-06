# Security

Warm Company generates 800 deterministic NFT DNA records for a charitable Chia campaign. A compromised seed, a flipped legal-title flag, or a silent generator change can mint the wrong collection.

## Please report

- Leakage or logging of the production seed
- Ways to flip `legal_title_to_physical_item` to true
- Ways to mint with the well-known development seed while `--mint` is set
- Supply, class-count, or goods-budget bypasses
- Dignity-label bypasses that would ship poverty-as-costume names
- Dependency or CI injection that could change `collection_fingerprint`

## Please do not

- Open a public issue that contains a production seed
- File a marketplace listing with invented IPFS/HTTP image URLs
- Treat a green local generate as a mint without `python -m warm_company preflight --mint`

## How to report

Use GitHub private vulnerability reporting on [FlipThisCrypto/warm-company](https://github.com/FlipThisCrypto/warm-company) when available. Otherwise contact the repository owners through the organization listed in `config/collection.json` (`Not By Chance Outreach`) without including secrets in the first message.

We will rotate a production seed if it may have been exposed, then regenerate and re-validate fingerprints before any mint.
