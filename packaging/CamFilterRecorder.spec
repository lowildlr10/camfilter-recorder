Name:           CamFilterRecorder
Version:        1.1.0
Release:        1%{?dist}
Summary:        Webcam recorder with real-time filters
License:        MIT
BuildArch:      x86_64

%description
CamFilter Recorder is a desktop application for recording webcam
or camera input with real-time filters including Night Vision,
Infrared/Thermal, Sepia, Cartoon, and more. Supports resolutions
from 240p up to 1080p.

%install
mkdir -p %{buildroot}/usr/local/bin
install -m 755 %{_builddir}/CamFilterRecorder %{buildroot}/usr/local/bin/CamFilterRecorder

mkdir -p %{buildroot}/usr/share/applications
cp %{_builddir}/camfilter-recorder.desktop %{buildroot}/usr/share/applications/camfilter-recorder.desktop

%files
/usr/local/bin/CamFilterRecorder
/usr/share/applications/camfilter-recorder.desktop

%changelog
* Sun May 10 2026 GitHub Actions <ci@github.com> - 1.1.0-1
- Add snapshot (Ctrl+S) feature: saves current filtered frame as PNG
- Refactor into MVC modules: controller, window, dialogs, constants
- Fix Pencil Sketch filter performance

* Sun May 10 2026 GitHub Actions <ci@github.com> - 1.0.0-1
- Initial RPM release
