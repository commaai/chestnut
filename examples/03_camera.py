import argparse
import asyncio
from pathlib import Path
import cv2
from vision import Vision


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


async def main():
  parser = argparse.ArgumentParser(description='YOLO26 on a webcam, video, or comma camera.')
  parser.add_argument('--source', default='0', help='Webcam, video/URL, or comma:road, comma:driver, comma:wide')
  parser.add_argument('--host', help='comma IP address')
  parser.add_argument('--model', choices=['yolo', 'segment'], default='yolo')
  parser.add_argument('--frames', type=int, default=10, help='Frames to save without preview')
  parser.add_argument('--preview', action='store_true', help='Show a live preview window')
  args = parser.parse_args()
  if args.source.startswith('comma') and not args.host: parser.error('--host is required for a comma camera')

  model = Vision(args.model)
  Path('frames').mkdir(exist_ok=True)
  comma_streams = {'comma': 'road', 'comma:road': 'road', 'comma:wide': 'wideRoad', 'comma:driver': 'driver'}
  if args.source in comma_streams:
    from teleop import frames
    stream = frames(args.host, comma_streams[args.source])
  else:
    stream = video_frames(args.source)
  print('Saving to frames/.', flush=True)
  try:
    i = 0
    while True:
      try: frame = await anext(stream) if args.source in comma_streams else next(stream)
      except (StopAsyncIteration, StopIteration): break
      result = model(frame)
      result.save(f'frames/{i:05d}.jpg')
      if args.preview:
        cv2.imshow('chestnut', result.plot())
        if cv2.waitKey(1) == 27: break
      print(f'Frame {i + 1}', flush=True)
      if not args.preview and i + 1 >= args.frames: break
      i += 1
  finally:
    await stream.aclose() if args.source in comma_streams else stream.close()
    if args.preview: cv2.destroyAllWindows()


if __name__ == '__main__':
  asyncio.run(main())
