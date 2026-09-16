import argparse
from pathlib import Path
import subprocess
import sys
import cv2
import numpy as np
from vision import Vision


def comma_frames(stream):
  checkout = Path('/data/openpilot')
  sys.path.append(str(checkout))
  from msgq.visionipc import VisionIpcClient
  process = None
  if subprocess.run(['pgrep', '-x', 'camerad'], stdout=subprocess.DEVNULL).returncode:
    process = subprocess.Popen([str(checkout / 'openpilot/system/camerad/camerad')],
                               cwd=checkout, stdout=subprocess.DEVNULL)
  try:
    client = VisionIpcClient('camerad', stream, True)
    client.connect(True)
    while True:
      buf = client.recv()
      if buf is None: continue
      y = np.ndarray((buf.height, buf.width), np.uint8, buf.data, strides=(buf.stride, 1))
      uv = np.ndarray((buf.height//2, buf.width//2, 2), np.uint8, buf.data,
                      offset=buf.uv_offset, strides=(buf.stride, 2, 1))
      yield cv2.cvtColorTwoPlane(y, uv, cv2.COLOR_YUV2BGR_NV12)
  finally:
    if process is not None:
      process.terminate()
      process.wait()


def video_frames(source):
  capture = cv2.VideoCapture(int(source) if source.isdecimal() else source)
  try:
    if not capture.isOpened(): raise RuntimeError(f'Cannot open {source}')
    while True:
      ok, frame = capture.read()
      if not ok: break
      yield frame
  finally:
    capture.release()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='YOLO26 on a webcam, video, or comma camera.')
  parser.add_argument('--source', default='0', help='Webcam, video/URL, or comma:road, comma:driver, comma:wide')
  parser.add_argument('--model', choices=['yolo', 'segment'], default='yolo')
  parser.add_argument('--frames', type=int, default=10, help='Frames to save without preview')
  parser.add_argument('--preview', action='store_true', help='Show a live preview window')
  args = parser.parse_args()

  model = Vision(args.model)
  Path('frames').mkdir(exist_ok=True)
  comma_streams = {'comma': 0, 'comma:road': 0, 'comma:wide': 1, 'comma:driver': 2}
  stream = comma_frames(comma_streams[args.source]) if args.source in comma_streams else video_frames(args.source)
  print('Saving to frames/.', flush=True)
  try:
    for i, frame in enumerate(stream):
      result = model(frame)
      result.save(f'frames/{i:05d}.jpg')
      if args.preview:
        cv2.imshow('chestnut', result.plot())
        if cv2.waitKey(1) == 27: break
      print(f'Frame {i + 1}', flush=True)
      if not args.preview and i + 1 >= args.frames: break
  finally:
    stream.close()
    if args.preview: cv2.destroyAllWindows()
