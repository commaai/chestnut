import argparse
import asyncio
import subprocess
from pathlib import Path
import cv2


def video_frames(source):
  for candidate in (0, 1) if source is None else (int(source) if source.isdecimal() else source,):
    capture = cv2.VideoCapture(candidate)
    ok, frame = capture.read()
    if capture.isOpened() and ok: break
    capture.release()
  else: raise RuntimeError(f'Cannot open {source or "a webcam"}')
  try:
    yield frame
    while True:
      ok, frame = capture.read()
      if not ok: break
      yield frame
  finally:
    capture.release()


async def main():
  parser = argparse.ArgumentParser(description='YOLO26 on a webcam, video, or comma camera.')
  parser.add_argument('--source', help='Webcam index, video/URL, or comma:road, comma:driver, comma:wide')
  parser.add_argument('--host', help='comma IP address or ~/.ssh/config host alias')
  parser.add_argument('--model', choices=['yolo', 'segment'], default='yolo')
  parser.add_argument('--frames', type=int, default=10, help='Frames to save without preview')
  parser.add_argument('--preview', action=argparse.BooleanOptionalAction, default=True, help='Show a live preview window')
  args = parser.parse_args()
  source = args.source or ('comma:wide' if args.host else None)
  if source and source.startswith('comma') and not args.host: parser.error('--host is required for a comma camera')

  Path('frames').mkdir(exist_ok=True)
  comma_streams = {'comma': 'road', 'comma:road': 'road', 'comma:wide': 'wideRoad', 'comma:driver': 'driver'}
  if source in comma_streams:
    from teleop import frames
    stream = frames(args.host, comma_streams[source])
  else:
    stream = video_frames(source)
  print('Connecting to comma...' if source in comma_streams else 'Opening camera...', flush=True)
  model = None
  try:
    i = 0
    while True:
      try: frame = await anext(stream) if source in comma_streams else next(stream)
      except (StopAsyncIteration, StopIteration): break
      if model is None:
        if args.preview:
          cv2.imshow('chestnut', frame)
          cv2.waitKey(1)
        print('Camera stream started', flush=True)
        from tinygrad import Context
        from vision import Vision
        print('Running first inference (can take a while)', flush=True)
        with Context(DEBUG=1):
          model = Vision(args.model)
          result = model(frame)
      else: result = model(frame)
      if not args.preview: result.save(f'frames/{i:05d}.jpg')
      if args.preview:
        cv2.imshow('chestnut', result.plot())
        if cv2.waitKey(1) == 27: break
      print(f'Frame {i + 1}', flush=True)
      if not args.preview and i + 1 >= args.frames: break
      i += 1
  finally:
    await stream.aclose() if source in comma_streams else stream.close()
    if args.preview: cv2.destroyAllWindows()


if __name__ == '__main__':
  try:
    asyncio.run(main())
  except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
    raise SystemExit(f'Error: {str(error) or type(error).__name__}') from None
  except KeyboardInterrupt:
    pass
