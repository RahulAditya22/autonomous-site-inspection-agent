# Models

AegisFleet uses Ultralytics YOLO11n as an optional local CPU object detector. The first inference may download `yolo11n.pt` if absent; the weight file is ignored by git. If unavailable, the app remains usable and explicitly reports that no visual claim was made.

The detector is COCO-trained, so only its supported general object categories are treated as directly observed. Site-specific hazards require a suitable trained/evaluated model before deployment claims.
