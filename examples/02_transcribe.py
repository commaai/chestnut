import argparse
import common
from examples.whisper import init_whisper, transcribe_file

parser = argparse.ArgumentParser(description="Transcribe speech locally with Whisper tiny.en.")
parser.add_argument("audio")
args = parser.parse_args()
model, tokenizer = init_whisper("tiny.en")
print(transcribe_file(model, tokenizer, args.audio))
