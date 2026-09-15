import argparse
import cv2
from vision import Vision

parser = argparse.ArgumentParser(description='YOLO26 detection and segmentation with tinygrad.')
parser.add_argument('image')
parser.add_argument('--model', choices=['yolo', 'segment'], default='yolo')
parser.add_argument('--output', default='result.jpg')
args = parser.parse_args()

image = cv2.imread(args.image)
if image is None: raise SystemExit(f'Cannot open {args.image}')
Vision(args.model)(image).save(args.output)
print(args.output)
