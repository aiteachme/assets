# AITeachMe Assets

Public assets consumed by AITeachMe.

```text
community/
  wechat-qr.jpg
demo-courses/
  atmx/
    *.atmx
  catalog/
    v1/
      index.json
```

## Updating the demo course catalog

After adding, replacing, or deleting `.atmx` files under `demo-courses/atmx/`, rebuild the catalog from the repository root:

```powershell
python scripts/update_demo_courses_catalog.py
git diff -- demo-courses/catalog/v1/index.json
```

The script reads each package's `manifest.json` and writes `demo-courses/catalog/v1/index.json`. It uses only the Python standard library and does not require command-line arguments, environment variables, or a separate configuration file. Its paths are fixed as follows:

- Input: `demo-courses/atmx/*.atmx`
- Output: `demo-courses/catalog/v1/index.json`

Commit the `.atmx` changes and the generated catalog together. Do not edit the generated catalog by hand.

Alternatively, after pushing the `.atmx` changes, run **Actions > Update Demo Courses Catalog > Run workflow** on GitHub, or use GitHub CLI:

```powershell
gh workflow run update-demo-courses-catalog.yml
```

The workflow runs the same script and commits the catalog only when it changes.

Keep demo packages small. GitHub rejects regular Git objects over 100 MB, so larger public packages should move to Releases or a real CDN later.
