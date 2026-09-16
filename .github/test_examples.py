import os
from pathlib import Path
import subprocess
import sys
import tempfile

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
os.environ['DEV'] = 'CPU'


def run(example, *args, cwd=ROOT):
  result = subprocess.run([sys.executable, str(ROOT / 'examples' / example), *args],
                          cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=900)
  print(result.stdout, flush=True)
  result.check_returncode()
  return result.stdout


for model in ('qwen3.5:0.8b', 'llama3.2:1b'):
  assert run('01_chat.py', '--model', model, '--benchmark', '3', '--max_context', '256').count('tok/s') == 3

image = cv2.imread(str(ROOT / 'zidane.jpg'))
assert image is not None
for model in ('yolo', 'segment'):
  with tempfile.TemporaryDirectory() as directory:
    folder = Path(directory)
    run('02_vision.py', str(ROOT / 'zidane.jpg'), '--model', model, '--output', str(folder / 'result.jpg'))
    annotated = cv2.imread(str(folder / 'result.jpg'))
    assert annotated is not None and annotated.shape == image.shape
    assert np.abs(annotated.astype(float) - image).mean() > 1
    for i in range(10):
      assert cv2.imwrite(str(folder / f'input-{i:05d}.jpg'), image)
    run('03_camera.py', '--source', str(folder / 'input-%05d.jpg'), '--model', model, cwd=folder)
    frames = sorted((folder / 'frames').glob('*.jpg'))
    assert len(frames) == 10
    for frame in frames:
      saved = cv2.imread(str(frame))
      assert saved is not None and saved.shape == image.shape

assert 'bow tie:' in run('04_classify.py').lower()
