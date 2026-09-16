import os
from pathlib import Path
import re
import sys
import sysconfig

if sys.platform == 'darwin':
  candidates = [Path(f'/opt/homebrew/opt/llvm@{version}/lib/libLLVM.dylib') for version in (21, 20, 19)]
else:
  directories = [Path('/usr/lib64'), Path('/usr/lib'), Path('/lib'), Path('/lib64'),
                 Path('/usr/lib') / sysconfig.get_config_var('MULTIARCH')]
  libraries = [path for directory in directories for path in directory.glob('libLLVM*') if path.is_file()]
  candidates = [path for version in (21, 20, 19) for path in libraries
                if re.search(rf'libLLVM(?:-|\.so\.){version}(?:\.so|\.|$)', path.name)]

library = next((path for path in candidates if path.is_file()), None)
if library is None:
  raise SystemExit('LLVM 19–21 was not found. Install its shared library and rerun setup.')

# Persist distro-specific LLVM paths for every .venv/bin/python command.
configuration = Path(sysconfig.get_path('purelib')) / 'chestnut_native.pth'
configuration.write_text(f'import os; os.environ.setdefault("LLVM_PATH", {str(library)!r})\n')
os.environ["LLVM_PATH"] = str(library)
os.environ["DEV"] = "CPU"

from tinygrad import Tensor
from tinygrad.runtime.autogen import libusb
from tinygrad.runtime.support.compiler_llvm import LLVMCompiler

assert libusb.libusb_get_version()
assert LLVMCompiler("AMDGPU", "gfx1200", "").compile('define amdgpu_kernel void @test() { ret void }')
assert Tensor([1, 2, 3, 4]).square().sum().item() == 30
print("CPU, LLVM, and libusb checked.")
