from pathlib import Path
import sys
import numpy as np
from tinygrad import Context
from ultralytics import YOLO
import torch
from torchvision.models import resnet18, ResNet18_Weights

folder = Path(__file__).resolve().parents[1] / 'models'
folder.mkdir(exist_ok=True)
for name in ('yolo26n', 'yolo26n-seg'):
  if not (folder / f'{name}.onnx').exists():
    YOLO(str(folder / f'{name}.pt')).export(format='onnx', imgsz=320, opset=17, simplify=False, device='cpu', nms=False)

if not (folder / 'resnet18.onnx').exists():
  model = resnet18(weights=ResNet18_Weights.DEFAULT).eval()
  torch.onnx.export(model, torch.zeros(1, 3, 224, 224), folder / 'resnet18.onnx',
                    input_names=['image'], output_names=['scores'], opset_version=17, dynamo=False)

sys.path.insert(0, str(folder.parent / 'examples'))
from vision import Vision
with Context(DEBUG=1):
  for name in ('yolo', 'segment'):
    model = Vision(name)
    model(np.zeros((320, 320, 3), dtype=np.uint8))
    model(np.zeros((320, 320, 3), dtype=np.uint8))
print('Models ready.', flush=True)
