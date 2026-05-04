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

After adding, replacing, or deleting `.atmx` files under `demo-courses/atmx/`, run the `Update Demo Courses Catalog` workflow manually. It rebuilds `demo-courses/catalog/v1/index.json` from package manifests and commits the catalog when it changes.

Keep demo packages small. GitHub rejects regular Git objects over 100 MB, so larger public packages should move to Releases or a real CDN later.
