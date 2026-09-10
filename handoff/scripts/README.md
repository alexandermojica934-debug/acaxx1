# ACASO Omniverse - Runner Scripts

These are the ACASO King runner scripts re-targeted at the live ACASO Omniverse
Council of Weavers engine (`POST /api/acaso/deliberate`).

| Script | What it does | Server preset |
|---|---|---|
| `script_01_genesis_engine.py` | Invents a new product/service and writes an invention brief `.md` | `genesis` |
| `script_03_sovereign_hunter.py` | Profiles 3 targets + bespoke outreach sequences, writes a package `.md` | `hunter` |
| `acaso_client.py` | Shared HTTP client / report writer | - |

```bash
pip install httpx
export ACASO_URL=https://contest-ready-app.preview.emergentagent.com   # or your own host
python script_01_genesis_engine.py
```

Every run is also journaled server-side and visible in the **Council** tab
(Past deliberations -> open / export / delete).

## Honesty note
The council is real multi-model reasoning (Gemini / GPT / Claude via the Emergent key) with a
Meta-Weaver synthesis. It has **no live market data, on-chain feeds or lead databases** connected;
"weak signals" are inferred, not measured. Nothing here is financial advice.
