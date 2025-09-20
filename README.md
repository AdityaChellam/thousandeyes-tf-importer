# thousandeyes-tf-importer
Zero-touch importer that scans ThousandEyes via the v7 API, normalizes test names, maps test types to Terraform resources, and emits per-test import blocks so you can bring existing tests under Terraform management. Supports org scoping, dry-run, and extensible type mappings.
