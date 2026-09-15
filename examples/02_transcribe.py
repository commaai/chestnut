import argparse
import common
from examples.whisper import init_whisper, transcribe_file

parser = argparse.ArgumentParser(description="Transcribe English speech with Whisper.")
parser.add_argument("audio")
parser.add_argument("--model", choices=["tiny.en", "base.en", "small.en", "medium.en"], default="tiny.en")
args = parser.parse_args()
model, tokenizer = init_whisper(args.model)
model.encoder.encode = model.encoder.__call__
print(transcribe_file(model, tokenizer, args.audio))
