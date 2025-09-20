
# thousandeyes-tf-importer

A practical utility to bring existing **ThousandEyes tests** under **Terraform** management. It discovers tests via the v7 API, normalizes names, maps test types to Terraform resources, and emits one **import block** per test for clean, repeatable onboarding.

---

## Why it matters

- **Eliminate config drift:** migrate UI-created tests to code.
- **Fast onboarding:** auto-generate import stanzas; no manual IDs.
- **Clean reviews:** one test = one file for tidy diffs.
- **Future-proof:** structured to add other resources later (alerts, labels).

---

## What it does

1. Prompts you to pick an **Account Group (AID)**.
2. Calls `/v7/tests?aid=<AID>`.
3. For each test:
   - extracts `testId`, `testName`, `type`
   - normalizes `testName` to a Terraform-safe identifier
   - maps `type` → Terraform resource (For example - `page-load` → `thousandeyes_page_load`)
   - writes a single `.tf` file with:
     ```hcl
     import {
       to = thousandeyes_<type>.<normalized_name>
       id = "<testId>"
     }
     ```

Output is written to `output/tests/`, one file per test, sorted deterministically.


https://github.com/user-attachments/assets/136fed3d-67d2-4c4f-a794-e423ac7230f8


---

## Prerequisites

- **Python** 3.9+
- **Terraform** 1.5.0+
- A **ThousandEyes user API token** with access to the target Account Group ID (AID)
- ThousandEyes Terraform provider (installed by `terraform init`)

Install Python deps:
```bash
pip install -r requirements.txt
```

---

## Step 1 — Configure the token for the Python generator

Open `te_tf_importer/config.py`:
```python
BASE_URL = "https://api.thousandeyes.com/v7"
TOKEN = "PASTE_YOUR_OAUTH_BEARER_TOKEN_HERE"  # Generated from the ThousandEyes Platform

# Default output folder
OUTPUT_DIR = "output"
```

> This token is for the **Python** generator only. Terraform will be configured separately.

---

## Step 2 — Generate import blocks

From the repo root:
```bash
python main.py

# or explicitly select the tests importer:
python main.py tests
```

- Select your **Account Group ID** (AID) when prompted.
- Inspect the generated files under `output/tests/`.

Example generated block:
```hcl
import {
  to = thousandeyes_page_load.example_homepage
  id = "1293181892321"
}
```

---

## Step 3 — Prepare a Terraform module

Create (or use) a Terraform module and copy the generated `.tf` files into it. Add a minimal provider:

```hcl
terraform {
  required_providers {
    thousandeyes = {
      source  = "thousandeyes/thousandeyes"
      version = ">= 3.0.0"
    }
  }
}

provider "thousandeyes" {
  token            = "PASTE_YOUR_OAUTH_BEARER_TOKEN"   # without "Bearer " prefix
  account_group_id = "AID_USED_ABOVE"
}
```

Initialize:
```bash
terraform init
```

---

## Step 4 — Import and generate resource configuration

Use import blocks to both import and scaffold config:
```bash
terraform plan -generate-config-out=generated_imports.tf
```
- Terraform fetches each referenced object and writes proposed resource blocks to `generated_imports.tf`.

Finalize the import:
```bash
terraform apply
```

You can then refactor the generated resources into your module as needed. After a successful import, the import files can be kept (repeatable onboarding) or removed.


https://github.com/user-attachments/assets/37061a1c-9571-47c4-b42e-794ef6833bea


---

## Troubleshooting (quick)

- **401 Unauthorized**: In the **Terraform provider**, use the **raw** token (no “Bearer ”) and the **correct AID**. Verify by importing a single resource with `-target=...`.
- **Missing files**: Some items may be missing required fields (`testId`, `testName`, `type`) or need a new type mapping.
- **Name collisions**: The tool auto-dedupes (`_1`, `_2`, …).

---

## Roadmap

- Importers for **alerts**, **tags**, **users** and additional resource types.

## Maintainers

- Aditya Chellam
