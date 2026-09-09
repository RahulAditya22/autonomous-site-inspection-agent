# Dataset and model policy

The runnable application uses YOLO11n pretrained on COCO. COCO is not bundled. It is appropriate for general objects where the actual COCO label set supports them; it does not justify claims for smoke, fire, structural defects, PPE compliance or other site-specific conditions.

For transfer learning, use a separately obtained, licensed dataset and pass its YAML to `scripts/train.py`. Record source, license, class list, image counts and evaluation metrics before making capability claims.
