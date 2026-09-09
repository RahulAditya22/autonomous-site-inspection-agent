from __future__ import annotations
from PIL import Image
from app.config import settings
class PerceptionAgent:
    def __init__(self): self._model=None; self.available=False
    def _load(self):
        if self._model is not None:return
        try:
            from ultralytics import YOLO
            self._model=YOLO(settings.vision_model); self.available=True
        except Exception: self._model=False; self.available=False
    def analyze(self,image_path,min_conf=None):
        self._load(); img=Image.open(image_path).convert('RGB')
        if not self.available:return {'detections':[],'image_width':img.width,'image_height':img.height,'notes':['Local object detector unavailable; no visual claim made.'],'source':'unavailable'}
        results=self._model.predict(source=image_path,conf=min_conf or settings.vision_confidence,device='cpu',verbose=False); detections=[]
        for result in results:
            boxes=getattr(result,'boxes',None)
            if boxes is None:continue
            for box,score,cls in zip(boxes.xyxy.tolist(),boxes.conf.tolist(),boxes.cls.tolist()):
                detections.append({'label':result.names[int(cls)],'confidence':round(float(score),3),'directly_observed':True,'inferred':False,'unknown':False,'bbox':[round(v,1) for v in box]})
        return {'detections':detections,'image_width':img.width,'image_height':img.height,'notes':[] if detections else ['No configured COCO objects were detected above the confidence threshold.'],'source':'YOLO11n/COCO'}
