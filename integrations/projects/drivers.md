# BCI Drivers (C++)

**Role**: cpp-bci · **Path**: `../drivers`

Native C++/C BCI drivers with Python bindings and a device registry.

## Integration surface

| Surface | Purpose |
|---|---|
| `muse_driver.cpp/.h/.py` | Muse headset driver |
| `qlb_arduino_driver.cpp/.h` | QLB Arduino/ring driver |
| `device_registry.py` | Device discovery |
| `CMakeLists.txt` | Build (make build) |

## Wiring into SOVEREIGN

- `hardware/bci-ring/driver_adapter.py` imports `qlb_arduino_driver`.
- `hardware/earbuds/driver_adapter.py` imports `muse_driver`.
- Built via `Makefile build` / `CMake`; used by the BCI module.
