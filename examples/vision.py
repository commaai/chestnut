import os
from pathlib import Path

os.environ.setdefault("DEV", "CPU")
os.environ.setdefault("XDG_CACHE_HOME", str(Path(__file__).resolve().parents[1] / ".cache"))

import numpy as np
import torch
from ultralytics.data.augment import LetterBox
from ultralytics.engine.results import Results
from ultralytics.utils import ROOT, YAML, ops
from tinygrad import Tensor, TinyJit
from tinygrad.nn.onnx import OnnxRunner

# tinygrad's examples/yolov8-onnx.py, with Ultralytics preprocessing and results.
class Vision:
  def __init__(self, model='yolo'):
    name = 'yolo26n-seg' if model == 'segment' else 'yolo26n'
    self.model = OnnxRunner(str(Path(__file__).resolve().parents[1] / 'models' / f'{name}.onnx'))
    self.input, spec = next(iter(self.model.graph_inputs.items()))
    self.shape = spec.shape[2:]
    self.letterbox = LetterBox(self.shape, auto=False)
    self.names = YAML.load(ROOT / 'cfg/datasets/coco8.yaml')['names']
    self.run = TinyJit(lambda x: tuple(y.realize() for y in self.model({self.input: x}).values()))

  def __call__(self, image):
    resized = self.letterbox(image=image)
    x = np.ascontiguousarray(resized[:, :, ::-1].transpose(2, 0, 1)[None], dtype=np.float32) / 255
    outputs = [torch.from_numpy(y.numpy()) for y in self.run(Tensor(x).realize())]
    boxes = outputs[0][0]
    assert boxes.shape[1] in (6, 38), "Expected a YOLO26 end-to-end export (nms=False)"
    boxes = boxes[boxes[:, 4] > 0.25]
    boxes[:, :4] = ops.scale_boxes(self.shape, boxes[:, :4], image.shape)
    masks = None
    if len(outputs) == 2 and len(boxes):
      masks = ops.process_mask_native(outputs[1][0], boxes[:, 6:], boxes[:, :4], image.shape[:2])
    return Results(image, path='', names=self.names, boxes=boxes[:, :6], masks=masks)
