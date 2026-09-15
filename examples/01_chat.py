import sys
import common
from tinygrad.llm.cli import main, models

models["qwen3.5:9b"] = "https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/3885219b6810b007914f3a7950a8d1b469d598a5/Qwen3.5-9B-Q4_K_M.gguf"
models["qwen3.5:0.8b"] = "https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/6ab461498e2023f6e3c1baea90a8f0fe38ab64d0/Qwen3.5-0.8B-Q8_0.gguf"
if not any(arg.startswith(("--model", "-m")) for arg in sys.argv[1:]): sys.argv += ["--model", "qwen3.5:0.8b"]
if not any(arg.startswith("--max_context") for arg in sys.argv[1:]): sys.argv += ["--max_context", "1024"]
main()
