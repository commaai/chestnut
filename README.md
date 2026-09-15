# chestnut

## Setup

```sh
./setup.sh
. .venv/bin/activate
python tools/usb.py
```

## Examples

Inference on Chestnut. First run downloads and compiles the models.

### Chat

Local chat with Qwen3.5

```sh
python examples/01_chat.py --model qwen3.5:0.8b
python examples/01_chat.py --model qwen3.5:9b
python examples/01_chat.py --max_context 2048
python examples/01_chat.py --benchmark 20
```

### Transcribe

Audio to English text with Whisper.

```sh
python examples/02_transcribe.py recording.wav --model tiny.en
python examples/02_transcribe.py recording.wav --model base.en
python examples/02_transcribe.py recording.wav --model small.en
python examples/02_transcribe.py recording.wav --model medium.en
```

### Openpilot

Driving model benchmark with synthetic inputs.

```sh
python examples/03_openpilot.py /data/openpilot/openpilot/selfdrive/modeld/models/driving_supercombo.onnx
```
