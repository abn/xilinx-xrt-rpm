Name:           xrt
Version:        2.21.75
Release:        1%{?dist}
Summary:        Xilinx Runtime (XRT) for AMD NPU
License:        Apache-2.0 AND GPLv2 AND MIT
URL:            https://github.com/Xilinx/XRT
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  git
BuildRequires:  systemd-devel
BuildRequires:  libdrm-devel
BuildRequires:  boost-devel
BuildRequires:  boost-static
BuildRequires:  json-glib-devel
BuildRequires:  libcurl-devel
BuildRequires:  libuuid-devel
BuildRequires:  rapidjson-devel
BuildRequires:  opencl-headers
BuildRequires:  ocl-icd-devel
BuildRequires:  pybind11-devel
BuildRequires:  python3-pybind11
BuildRequires:  python3-devel
BuildRequires:  pkgconfig
BuildRequires:  ncurses-devel
BuildRequires:  elfutils-devel
BuildRequires:  libyaml-devel
BuildRequires:  systemtap-sdt-devel
BuildRequires:  openssl-devel
BuildRequires:  protobuf-compiler
BuildRequires:  protobuf-devel
BuildRequires:  glibc-static
BuildRequires:  libstdc++-static
BuildRequires:  zlib-static

%description
Xilinx Runtime (XRT) for AMD NPU devices.

%package base
Summary:        Xilinx Runtime base user-space libraries and utilities
Provides:       xrt-base = %{version}-%{release}

%description base
Xilinx Runtime base user-space libraries and utilities.

%package npu
Summary:        Xilinx Runtime NPU support
Requires:       %{name}-base%{?_isa} = %{version}-%{release}
Provides:       xrt-npu = %{version}-%{release}

%description npu
Xilinx Runtime specific support modules for NPU.

%package -n xrt-plugin-amdxdna
Summary:        XRT plug-in for AMD XDNA NPU driver
Requires:       %{name}-base%{?_isa} = %{version}-%{release}
Provides:       xrt-plugin-amdxdna = %{version}-%{release}

%description -n xrt-plugin-amdxdna
This package contains the vital libxrt_driver_xdna.so shim that bridges XRT to the kernel's auto-loaded nodes.

%package devel
Summary:        Xilinx Runtime development headers and files
Requires:       %{name}-base%{?_isa} = %{version}-%{release}
Provides:       xrt-devel = %{version}-%{release}

%description devel
Development headers and libraries for Xilinx Runtime (XRT).

%prep
%autosetup -n %{name}-%{version}

%build
# 1. Build XRT
pushd xdna-driver/xrt/build
./build.sh -npu -opt -noctest -noinit -install_prefix /opt/xilinx/xrt
popd

# 2. Build xrt-plugin-amdxdna
pushd xdna-driver
mkdir build_plugin
cd build_plugin
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/opt/xilinx/xrt \
      -DSKIP_KMOD=ON \
      -DBUILD_VXDNA=ON \
      -DXRT_UPSTREAM=OFF \
      -DXRT_SUBMOD_SOURCE_DIR=xrt \
      ..
make -j$(nproc)
make DESTDIR=$PWD/install_root install
popd

%install
# Create buildroot directories
mkdir -p %{buildroot}/opt/xilinx/xrt

# 1. Copy XRT files from build/Release
cp -a xdna-driver/xrt/build/Release/opt/xilinx/xrt/* %{buildroot}/opt/xilinx/xrt/

# 2. Copy XRT Plugin files
cp -a xdna-driver/build_plugin/install_root/opt/xilinx/xrt/* %{buildroot}/opt/xilinx/xrt/

%files base
%dir /opt/xilinx
%dir /opt/xilinx/xrt
/opt/xilinx/xrt/bin/
/opt/xilinx/xrt/lib
/opt/xilinx/xrt/lib64/libxilinxopencl.so.2*
/opt/xilinx/xrt/lib64/libxrt++.so.2*
/opt/xilinx/xrt/lib64/libxrt_core.so.2*
/opt/xilinx/xrt/lib64/libxrt_coreutil.so.2*
/opt/xilinx/xrt/setup.*
/opt/xilinx/xrt/share/completions/
/opt/xilinx/xrt/share/doc/
/opt/xilinx/xrt/version.json
/etc/OpenCL/vendors/xilinx.icd

%files npu
/opt/xilinx/xrt/lib64/libxdp_core.so.2*
/opt/xilinx/xrt/lib64/xrt/

%files -n xrt-plugin-amdxdna
/opt/xilinx/xrt/lib64/libxrt_driver_xdna.so.2*
/opt/xilinx/xrt/lib64/libvxdna.so.1*

%files devel
/opt/xilinx/xrt/include/
/opt/xilinx/xrt/lib64/libxilinxopencl.so
/opt/xilinx/xrt/lib64/libxrt++.so
/opt/xilinx/xrt/lib64/libxrt_core.so
/opt/xilinx/xrt/lib64/libxrt_coreutil.so
/opt/xilinx/xrt/lib64/libvxdna.so
/opt/xilinx/xrt/lib64/libaiebu.a
/opt/xilinx/xrt/lib64/libcert_dtrace.a
/opt/xilinx/xrt/lib64/libxilinxopencl.a
/opt/xilinx/xrt/lib64/libxrt++.a
/opt/xilinx/xrt/lib64/libxrt_core.a
/opt/xilinx/xrt/lib64/libxrt_coreutil.a
/opt/xilinx/xrt/lib64/pkgconfig/
/opt/xilinx/xrt/share/cmake/


%changelog
* Tue Jun 02 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 2.21.75-1
- Initial unified packaging of XRT base, npu, plugin, and devel
