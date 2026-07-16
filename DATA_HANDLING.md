# Data handling

This repository is a static, public toy project. Forking or cloning it does
not send code or telemetry to Veripsa, and the upstream repository does not
run anything on your behalf.

Data reaches Veripsa Core only if you install the GitHub App on your fork (or
another repository you control). GitHub then sends events for the repositories
you selected. Veripsa may read repository files and diff data transiently to
produce its advisory, but it does not retain or display source file bodies or
diff bodies. GitHub secret-store values are not exposed to the App and are
never available to read. A committed `.env`-style or other configuration file
may be read transiently, but its body and values are not retained.

Content-free metadata may be retained, including GitHub identifiers and public
handles; repository, PR, branch, ref, path, line-range, configuration-key,
schema, language, and symbol names; named relationships; fingerprints; and the
operational state needed for checks, comments, delivery, and lifecycle
handling. Names and public handles can still contain personal or customer
information, so Veripsa treats them as scoped customer data.

The canonical contract below lists every retained category, retention window,
and the difference between uninstall and account erasure. That contract is the
source of truth; this lab intentionally does not duplicate its full table.

For the complete boundary and deletion choices, see:

- [Veripsa public data-handling contract](https://github.com/GetVeripsa/veripsa-webhook-spec/blob/main/DATA_HANDLING.md)
- [Privacy Policy](https://veripsa.com/privacy)
- [Trust Center](https://veripsa.com/trust)
- [Vulnerability disclosure](https://veripsa.com/security/disclosure)

This document intentionally describes the data boundary, not Veripsa's private
analysis, ranking, or scoring methods.
