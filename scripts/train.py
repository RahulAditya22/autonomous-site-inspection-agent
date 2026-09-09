"""CPU-friendly transfer-learning entry point. Supply a licensed dataset YAML."""
import argparse
p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--epochs',type=int,default=5);a=p.parse_args()
from ultralytics import YOLO
YOLO('yolo11n.pt').train(data=a.data,epochs=a.epochs,imgsz=640,device='cpu',workers=0)
