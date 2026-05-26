# @true-review/shared

Cross-platform type definitions. The canonical schema lives here so web (TypeScript), API (Pydantic), and iOS (Swift) stay aligned.

## Files

- `schema.json` — JSON Schema source of truth for the API surface.
- `types.ts` — Hand-mirrored TS types (consumed by the Next.js app).
- `Types.swift` — Hand-mirrored Swift structs (consumed by the iOS app).

When you add a new endpoint or model, update all three. The API's Pydantic models in `api/app/schemas.py` are the runtime contract.
