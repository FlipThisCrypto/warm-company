# Config schema notes

Executable truth is the JSON in `/config`. This folder documents the shapes so a later CHIP or web UI does not invent fields.

## Token DNA (generator output)

```json
{
  "token_id": 1,
  "pre_id": 17,
  "class_id": "sleeping-bag",
  "dna": "hex sha256",
  "special": false,
  "traits": {
    "background": "winter-sunrise",
    "body": "ember-rust"
  }
}
```

`class_id` is one of `sleeping-bag`, `small-tent`, `large-tent`.
`traits` keys are slot ids from `traits.json`.
`dna` is `sha256(class + sorted "slot=value")`.

## CHIP-0007 (metadata output)

Required: `format=CHIP-0007`, `name`, `description`.
Used: `minting_tool`, `sensitive_content=false`, `series_number`, `series_total=800`, `attributes[]`, `collection{id,name,attributes}`, `data`.

`collection.id` is a UUID for off-chain grouping. It is **not** a Chia launcher id.

`data.legal_title_to_physical_item` must remain `false` unless counsel later says otherwise.

Do not add live image URLs until they exist.
