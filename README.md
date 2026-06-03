# xrt-rpm

Fedora RPM packages for [XRT (Xilinx Runtime)](https://github.com/Xilinx/XRT) and the AMD XDNA user-space runtime plugin.

The source is integrated via git submodule from [amd/xdna-driver](https://github.com/amd/xdna-driver).

## Package Breakdown

This spec configures a unified build of the following packages:
- **`xrt-base`**: Core XRT user-space runtime libraries and diagnostics utility (`xrt-smi`).
- **`xrt-npu`**: Specific XDP core profile and NPU tracing modules.
- **`xrt-plugin-amdxdna`**: The `libxrt_driver_xdna.so` shim connecting XRT to the kernel's upstreamed `amdxdna` driver node.
- **`xrt-devel`**: Development headers, static archives, and CMake target configurations.
- **`python3-xrt`**: Python bindings for XRT (`pyxrt`).

## Installation

These packages are targeted for Fedora 44+.

```bash
# Enable the Copr repository (substitute your repository name)
sudo dnf copr enable abn/amd-npu

# Install runtime components
sudo dnf install xrt-base xrt-npu xrt-plugin-amdxdna

# Download and install the validation firmware archive for your NPU platform (required for xrt-smi validate)
# Supported archives: xrt_smi_phx.a, xrt_smi_strx.a, xrt_smi_npu3.a, xrt_smi_ve2.a
sudo smi_install_archive.sh xrt_smi_strx.a 2.25.0

# Install development files (optional)
sudo dnf install xrt-devel python3-xrt
```

## Post-Installation Host Configuration

The NPU runtime requires unprivileged huge buffer mapping into system memory. You must increase the host's memory locking (`memlock`) limits.

Create a configuration drop-in:

```ini
# /etc/security/limits.d/99-amdxdna.conf
* soft memlock unlimited
* hard memlock unlimited
```

*Without this limits override, XRT allocations will crash immediately upon buffer object (BO) instantiation.*

## Development

This project uses [tito](https://github.com/rpm-software-management/tito) for versioning and package release management.

### Containerized Builds (Recommended)

To build RPMs locally using Podman without polluting the host environment:

```bash
# Start the builder container
podman run -d --rm -i --name rpmbuilder-xrt \
  -v ${PWD}:/sources:z \
  quay.io/abn/rpmbuilder:fedora-44 sleep inf

# Run tito build inside the container
podman exec rpmbuilder-xrt rpmbuilder
```

Output RPMs are placed in the container `/output/` folder and can be copied back:
```bash
podman cp rpmbuilder-xrt:/output/. ./output/
```

### Tagging a Release

To tag a new version:
```bash
tito tag
```
