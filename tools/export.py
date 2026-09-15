from pathlib import Path
from ultralytics import YOLO

folder = Path(__file__).resolve().parents[1] / 'models'
folder.mkdir(exist_ok=True)
for name in ('yolo26n', 'yolo26n-seg'):
  if not (folder / f'{name}.onnx').exists():
    YOLO(str(folder / f'{name}.pt')).export(format='onnx', imgsz=320, opset=17, simplify=False, device='cpu', nms=False)
