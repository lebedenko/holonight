# Qt hashing mechanism diagnostic

Standalone host Qt Core Release executable. See
[protocol](../../docs/sdd/preview-hash-device-mechanism.md).

```sh
python3 scripts/run-preview-hash-device-mechanism.py \
  --audit build/preview-hash-device-path-20261116-15 \
  --verification build/preview-hash-device-path-20261116-15-independent.json \
  --output build/preview-hash-device-mechanism-20261116-01
python3 scripts/verify-preview-hash-device-mechanism.py \
  --evidence build/preview-hash-device-mechanism-20261116-01 \
  --output build/preview-hash-device-mechanism-20261116-01-independent.json
```

Destinations must be fresh. One run only; failed evidence stays sealed. No
production code, runtime integrity policy or historical experiment is changed.
