# chestnut

## Setup

```sh
./setup.sh
. .venv/bin/activate
python tools/usb.py
```

## Examples

```sh
# First run downloads models and compiles kernels.
python examples/01_chat.py
python examples/02_transcribe.py recording.wav

# Bench inference only. Adjust the openpilot model path on PC.
python examples/03_openpilot.py /data/openpilot/openpilot/selfdrive/modeld/models/driving_supercombo.onnx
```
