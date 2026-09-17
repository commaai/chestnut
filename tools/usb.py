"""Checks if chestnut is connected and working"""
import os
os.environ.setdefault("DEV", "USB+AMD")
from tinygrad import Device, Tensor
from tinygrad.helpers import DEV
from tinygrad.runtime.support.usb import USB3

devices = USB3.list_devices(0x3801, 0x0001) + USB3.list_devices(0xADD1, 0x0001)
if not devices: raise SystemExit("No Chestnut found. Check power and USB.")
print([address for _, address in devices])
assert Device.DEFAULT == "AMD" and DEV.target("AMD").interface == "USB", "Use DEV=USB+AMD"
values = Tensor([1, 2, 3, 4])
assert (values * values).sum().item() == 30
print("Chestnut GPU check passed.")
