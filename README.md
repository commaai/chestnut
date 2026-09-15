# chestnut

Examples run on PC and Chestnut.

![Chestnut connections](chestnut.png)

## Setup

```sh
./setup.sh
```

Installs dependencies

**Device: `DEV=CPU` (PC, default) or `DEV=USB+AMD:LLVM` (Chestnut).**

### Chat

```sh
.venv/bin/python examples/01_chat.py
DEV=USB+AMD:LLVM .venv/bin/python examples/01_chat.py
```

Llama 3.2 1B, tinygrad's default chat model.

### YOLO

```sh
.venv/bin/python examples/02_vision.py bus.jpg --output boxes.jpg
.venv/bin/python examples/02_vision.py bus.jpg --model segment --output masks.jpg
```

YOLO26 detection and segmentation masks.

### Camera

```sh
.venv/bin/python examples/03_camera.py --source 0
.venv/bin/python examples/03_camera.py --source video.mp4 --model segment
```

Source can be webcam, video, or stream URL. Saves annotated images to `frames/`.

```sh
DEV=USB+AMD:LLVM .venv/bin/python examples/03_camera.py --source comma
DEV=USB+AMD:LLVM .venv/bin/python examples/03_camera.py --source comma --model segment
```

Uses openpilot’s camera stream.

### Check Chestnut

```sh
.venv/bin/python tools/usb.py
```

Finds Chestnut over USB and verifies a calculation on its GPU. For `PCIe link not up`, check GPU power

### Benchmark PC vs Chestnut

```sh
.venv/bin/python tools/benchmark.py models/yolo26n.onnx
DEV=USB+AMD:LLVM .venv/bin/python tools/benchmark.py models/yolo26n.onnx
```

Use `models/yolo26n-seg.onnx` for segmentation, or pass another ONNX model.

| Model | PC CPU | Chestnut | Speedup |
| --- | ---: | ---: | ---: |
| YOLO26n | 524.57 ms | 15.12 ms | 35× |
| YOLO26n-seg | 705.44 ms | 16.44 ms | 43× |

320×320 FP32, model inference only. PC: Threadripper PRO 5945WX.
