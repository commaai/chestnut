# chestnut

Run llm, object detection, and segmentation with tinygrad on your PC or chestnut.

## Setup

```sh
git clone https://github.com/commaai/chestnut.git
cd chestnut
./setup.sh
```

## Run on Chestnut

Plug in the 12V power and connect the USB3 cable from the USB3.2 port to your PC or comma.

![Chestnut connections](chestnut.png)

Check the connection:

```sh
.venv/bin/python tools/usb.py
```

Expected: `Chestnut GPU check passed.`

Examples default to `DEV=CPU` to run on PC.
Prefix any example command with `DEV=USB+AMD:LLVM` to use Chestnut.

## Examples

### Chat

```sh
.venv/bin/python examples/01_chat.py
.venv/bin/python examples/01_chat.py --model llama3.2:1b
```

Starts an interactive chat with Qwen 3.5 0.8B by default, or Llama 3.2 1B with `--model llama3.2:1b`. Models download on first run.

### YOLO

Detect objects or draw segmentation masks on a sample image. Open `boxes.jpg` or `masks.jpg` to see the result.

```sh
.venv/bin/python examples/02_vision.py zidane.jpg --output boxes.jpg
.venv/bin/python examples/02_vision.py zidane.jpg --model segment --output masks.jpg
```

### Camera: YOLO26 detection and segmentation

Runs YOLO26 on webcam frames. Detection draws labeled boxes. `--model segment` adds masks around each object.
Saves 10 annotated frames to `frames/` without a live preview. Use `--frames 100` for more.

```sh
.venv/bin/python examples/03_camera.py --source 0
.venv/bin/python examples/03_camera.py --source 0 --model segment
```

`--source` also accepts a video path or stream URL.

On a comma device with openpilot installed at `/data/openpilot`, use its camera stream:

```sh
DEV=USB+AMD:LLVM .venv/bin/python examples/03_camera.py --source comma
DEV=USB+AMD:LLVM .venv/bin/python examples/03_camera.py --source comma --model segment
```

## Performance
PC CPU: Threadripper PRO 5945WX

| Model | PC CPU | Chestnut | Speedup |
| --- | ---: | ---: | ---: |
| YOLO26n | 524.57 ms | 15.12 ms | 35× |
| YOLO26n-seg | 705.44 ms | 16.44 ms | 43× |


### Chat

| Model | PC CPU | Chestnut | Speedup |
| --- | ---: | ---: | ---: |
| Qwen 3.5 0.8B (Q8_0) | 2.96 tokens/s | 44.90 tokens/s | 15.2× |
| Llama 3.2 1B Instruct (Q6_K) | 0.91 tokens/s | 24.93 tokens/s | 27.2× |
