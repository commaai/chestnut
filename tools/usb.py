from tinygrad.runtime.support.usb import USB3

devices = USB3.list_devices(0x3801, 0x0001) + USB3.list_devices(0xADD1, 0x0001)
if not devices:
  raise SystemExit("No Chestnut found. Check its power and USB cable.")
print(f"Found {len(devices)} Chestnut(s): {[address for _, address in devices]}")
