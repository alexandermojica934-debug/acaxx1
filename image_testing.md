## TEST AGENT PROMPT – IMAGE INTEGRATION RULES ##
- Always use base64-encoded images (JPEG/PNG/WEBP only). No SVG/BMP/HEIC.
- Never upload blank / solid-color / uniform images; every image must contain real visual features.
- Re-detect MIME after any transformation; extract first frame of animated images; resize oversized images.
