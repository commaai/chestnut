# chestnut

Run chat, object detection, segmentation, and image classification with tinygrad on your PC or chestnut.

## Setup

```sh
git clone https://github.com/commaai/chestnut.git
cd chestnut
./setup.sh
```

## Run on PC

Activate the environment in each new terminal:

```sh
source .venv/bin/activate
```

These commands run on your PC's CPU.

### Chat

Chat with Qwen 3.5 0.8B (default) or Llama 3.2 1B. Models download on first run.

```sh
python examples/01_chat.py
python examples/01_chat.py --model llama3.2:1b
```

### YOLO

Detect objects or draw segmentation masks.

```sh
python examples/02_vision.py zidane.jpg --output boxes.jpg
python examples/02_vision.py zidane.jpg --model segment --output masks.jpg
```

### Camera

Run YOLO26 detection or segmentation on a webcam.
Use `--frames 100` for more. `--source` also accepts a video path or stream URL.

```sh
python examples/03_camera.py --source 0
python examples/03_camera.py --source 0 --model segment
```

### Image classification

Print the five most likely labels with ResNet18.

```sh
python examples/04_classify.py
python examples/04_classify.py zidane.jpg
```

## Run on chestnut

Plug in the 12V power and connect the USB3 cable from chestnut's USB3.2 port to your PC or comma.

![chestnut connections](chestnut.png)

In the activated environment, check the connection:

```sh
python tools/usb.py
```

Expected: `chestnut GPU check passed.`

Prefix any example command with `DEV=USB+AMD:LLVM` to run it on chestnut's GPU:

```sh
DEV=USB+AMD:LLVM python examples/01_chat.py
DEV=USB+AMD:LLVM python examples/02_vision.py zidane.jpg --output boxes.jpg
DEV=USB+AMD:LLVM python examples/03_camera.py --source 0
```

## Comma camera

On a comma device, run setup and activate the environment as above. Requires openpilot at `/data/openpilot`.
Select the road, driver, or wide road camera with `--source comma:road`, `comma:driver`, or `comma:wide`.

```sh
# Comma CPU
python examples/03_camera.py --source comma:road
python examples/03_camera.py --source comma:driver
python examples/03_camera.py --source comma:wide

# chestnut GPU connected to comma
DEV=USB+AMD:LLVM python examples/03_camera.py --source comma:road
DEV=USB+AMD:LLVM python examples/03_camera.py --source comma:driver
DEV=USB+AMD:LLVM python examples/03_camera.py --source comma:wide
```

## Performance

PC CPU: Threadripper PRO 5945WX. Comma CPU: Qualcomm SDM845.

| Model | PC CPU | Comma CPU | chestnut GPU |
| --- | ---: | ---: | ---: |
| YOLO26n | 526.07 ms | 1846.42 ms | 7.02 ms |
| YOLO26n-seg | 704.56 ms | 2349.27 ms | 7.98 ms |
| ResNet18 | 246.52 ms | 610.91 ms | 11.98 ms |
| Qwen 3.5 0.8B (Q8_0) | 2.98 tokens/s | 0.76 tokens/s | 45.46 tokens/s |
| Llama 3.2 1B Instruct (Q6_K) | 0.94 tokens/s | 0.34 tokens/s | 25.21 tokens/s |
