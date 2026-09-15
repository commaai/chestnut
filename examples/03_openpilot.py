import argparse
import time
import numpy as np
import common
from tinygrad import Device, Tensor, TinyJit, Context
from tinygrad.nn.onnx import OnnxRunner

parser = argparse.ArgumentParser(description="Run an openpilot ONNX model on synthetic bench inputs.")
parser.add_argument("model", help="Path to driving_supercombo.onnx from your openpilot checkout")
args = parser.parse_args()
model = OnnxRunner(args.model)
inputs = {name: Tensor.zeros(*(dim if isinstance(dim, int) else 1 for dim in spec.shape), dtype=spec.dtype).realize()
          for name, spec in model.graph_inputs.items()}

@TinyJit
def run(**inputs):
  return {name: value.realize() for name, value in model(inputs).items()}

with Context(OPENPILOT_HACKS=1):
  for iteration in range(4):
    start = time.perf_counter()
    outputs = run(**inputs)
    Device[Device.DEFAULT].synchronize()
    print(f"Run {iteration}: {time.perf_counter() - start:.3f}s", flush=True)
for name, value in outputs.items():
  if not np.isfinite(value.numpy()).all(): raise RuntimeError(f"Non-finite output: {name}")
  print(name, value.shape)
