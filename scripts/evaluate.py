import argparse
p=argparse.ArgumentParser();p.add_argument('--data',required=True);a=p.parse_args()
from ultralytics import YOLO
print(YOLO('yolo11n.pt').val(data=a.data,device='cpu'))
