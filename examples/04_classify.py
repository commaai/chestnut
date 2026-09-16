import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('DEV', 'CPU')
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))

from PIL import Image
from torchvision.models import ResNet18_Weights
from tinygrad import Tensor
from tinygrad.helpers import fetch
from tinygrad.nn.onnx import OnnxRunner

parser = argparse.ArgumentParser(description='Classify an image with ResNet18.')
parser.add_argument('image', nargs='?')
args = parser.parse_args()
image = Image.open(args.image or fetch('https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg')).convert('RGB')
weights = ResNet18_Weights.DEFAULT
inputs = weights.transforms()(image).unsqueeze(0).numpy()
model = OnnxRunner(str(ROOT / 'models/resnet18.onnx'))
scores = model({'image': Tensor(inputs)})['scores'].softmax().numpy()[0]
for i in scores.argsort()[-5:][::-1]:
  print(f"{weights.meta['categories'][i]}: {scores[i]:.1%}")
