Name:           xrt
Version:        2.21.75
Release:        4%{?dist}
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

%package -n python3-xrt
Summary:        Python 3 bindings for Xilinx Runtime
Requires:       %{name}-base%{?_isa} = %{version}-%{release}
Provides:       python3-xrt = %{version}-%{release}

%description -n python3-xrt
Python 3 bindings for Xilinx Runtime (XRT).

%prep
%autosetup -n %{name}-%{version}

%build
# Fix upstream CMake 4 detection bug by overriding path for cmake3
mkdir -p bin
ln -sf /usr/bin/cmake bin/cmake3
export PATH=$PWD/bin:$PATH

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

# Copy etc/ OpenCL vendors file if it exists
if [ -d xdna-driver/xrt/build/Release/etc ]; then
    mkdir -p %{buildroot}/etc
    cp -a xdna-driver/xrt/build/Release/etc/* %{buildroot}/etc/
fi

# 2. Copy XRT Plugin files
cp -a xdna-driver/build_plugin/install_root/opt/xilinx/xrt/* %{buildroot}/opt/xilinx/xrt/

# Create wrapper scripts in /usr/bin to avoid wrapper path resolution issues when symlinked
mkdir -p %{buildroot}%{_bindir}
cat << 'EOF' > %{buildroot}%{_bindir}/xrt-smi
#!/bin/sh
exec /opt/xilinx/xrt/bin/xrt-smi "$@"
EOF
chmod +x %{buildroot}%{_bindir}/xrt-smi

cat << 'EOF' > %{buildroot}%{_bindir}/xclbinutil
#!/bin/sh
exec /opt/xilinx/xrt/bin/xclbinutil "$@"
EOF
chmod +x %{buildroot}%{_bindir}/xclbinutil

# Install smi_install_archive.sh script
cp xdna-driver/xrt/src/runtime_src/core/tools/xbutil2/smi_install_archive.sh %{buildroot}/opt/xilinx/xrt/bin/
chmod +x %{buildroot}/opt/xilinx/xrt/bin/smi_install_archive.sh

# Create wrapper script for smi_install_archive.sh in /usr/bin/
cat << 'EOF' > %{buildroot}%{_bindir}/smi_install_archive.sh
#!/bin/sh
exec /opt/xilinx/xrt/bin/smi_install_archive.sh "$@"
EOF
chmod +x %{buildroot}%{_bindir}/smi_install_archive.sh

# Register dynamic library path in ldconfig
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "/opt/xilinx/xrt/lib64" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/xrt-x86_64.conf

# Python path configuration file
mkdir -p %{buildroot}%{python3_sitearch}
echo "/opt/xilinx/xrt/python" > %{buildroot}%{python3_sitearch}/xrt.pth


%files base
%dir /opt/xilinx
%dir /opt/xilinx/xrt
/opt/xilinx/xrt/bin/
/opt/xilinx/xrt/lib
/opt/xilinx/xrt/lib64/libxilinxopencl.so.2*
/opt/xilinx/xrt/lib64/libxrt++.so.2*
/opt/xilinx/xrt/lib64/libxrt_core.so.2*
/opt/xilinx/xrt/lib64/libxrt_coreutil.so.2*
%{_bindir}/xrt-smi
%{_bindir}/xclbinutil
%{_bindir}/smi_install_archive.sh
%{_sysconfdir}/ld.so.conf.d/xrt-x86_64.conf
/opt/xilinx/xrt/setup.*
/opt/xilinx/xrt/share/completions/
/opt/xilinx/xrt/share/doc/
/opt/xilinx/xrt/version.json
/opt/xilinx/xrt/license/
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

%files -n python3-xrt
/opt/xilinx/xrt/python/
%{python3_sitearch}/xrt.pth



%changelog
* Wed Jun 03 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 2.21.75-4
- Use shell wrappers instead of symlinks in /usr/bin to resolve path issues

* Wed Jun 03 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 2.21.75-3
- Add system-wide integrations for binaries, ldconfig, and python

* Tue Jun 02 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 2.21.75-2
- Fix CMake 4 detection bug in Fedora 44+

* Tue Jun 02 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 2.21.75-1
- Initial unified packaging of XRT base, npu, plugin, and devel
