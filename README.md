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
      display-order.json
      index.json
```

## Updating the demo course catalog

After adding, replacing, or deleting `.atmx` files under `demo-courses/atmx/`, rebuild the catalog from the repository root:

```powershell
python scripts/update_demo_courses_catalog.py
git diff -- demo-courses/catalog/v1/index.json
```

The script reads each package's `manifest.json` and writes `demo-courses/catalog/v1/index.json`. It uses only the Python standard library and does not require command-line arguments or environment variables. Its paths are fixed as follows:

- Input: `demo-courses/atmx/*.atmx`
- Display order: `demo-courses/catalog/v1/display-order.json`
- Output: `demo-courses/catalog/v1/index.json`

The `packages` list in `display-order.json` is read from top to bottom and appears on the AITeachMe home page from left to right, then row by row. To move an existing course, move its package filename in that list. New `.atmx` files do not need to be added immediately: unlisted courses are appended after configured courses in a deterministic course-name order. Removing or renaming a listed package requires updating the order file so stale entries fail loudly instead of silently changing the home page.

Commit the `.atmx` changes, `display-order.json` changes, and the generated catalog together. Do not edit the generated catalog by hand.

Alternatively, after pushing the `.atmx` changes, run **Actions > Update Demo Courses Catalog > Run workflow** on GitHub, or use GitHub CLI:

```powershell
gh workflow run update-demo-courses-catalog.yml
```

The workflow runs the same script and commits the catalog only when it changes.

Keep demo packages small. GitHub rejects regular Git objects over 100 MB, so larger public packages should move to Releases or a real CDN later.
