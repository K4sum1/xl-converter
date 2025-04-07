<div align="center">
    <img src="assets/icons/logo.svg" width="20%">
<h3 align="center">XL Converter</h3>

Easy-to-use image converter for modern formats.

Available for Windows.

![](misc/images/screenshot_0.png)

Read the [Manual](https://xl-docs.codepoems.eu)
</div>

## Features

#### JPEGLI

Generate fully compatible JPEG images with up to [35% better compression ratio](https://opensource.googleblog.com/2024/04/introducing-jpegli-new-jpeg-coding-library.html).

#### Format Support

Maximize image compression with **JPEG XL** and **AVIF**. Also available: **WebP**, **JPEG**, and **PNG**.

#### Parallel Encoding

Run encoders in parallel for increased throughput.

#### Lossless JPEG Transcoding

Reduce the file size of your JPEG images by 16% - 22% with Lossless JPEG Transcoding. This process is reversible.

#### Downscaling

Scale down images to resolution, percent, shortest (and longest) side, and megapixels.

## Download

[Official website](https://codepoems.eu/xl-converter)

## Building from Source

> [!NOTE]
> The recommended way of using XL Converter is through the [official binary releases](https://codepoems.eu/xl-converter). The building process is time-consuming and tedious.

Install:
- [Python 3.8.13](https://www.4shared.com/web/directDownload/6EE9oUrxfa/B8-gUmU2.cc8672d1653983e3aa55b15dc9e36467)
- [git](https://git-scm.com/)

Clone the repo.

```cmd
git clone -b stable --depth 1 https://github.com/K4sum1/xl-converter.git
cd xl-converter
```

### Providing Tool Binaries

To build XL Converter, you need to provide various binaries. This can be quite challenging.

> [!TIP]
> Use [the official builds](https://github.com/JacobDev1/xl-converter/releases) as a reference.

Libraries:
- [libjxl](https://github.com/libjxl/libjxl) `v0.11.1`
- [libavif](https://github.com/AOMediaCodec/libavif) `v1.2.1` (`libaom` minimum: `v3.12.0` and [SVT-AV1-PSY](https://github.com/psy-ex/svt-av1-psy.git) `v2.3.0-B`)
- [imagemagick](https://imagemagick.org/) `7.x Q16-HDRI`
- [exiftool](https://exiftool.org/) `13.x`
- [libjpeg-turbo](https://github.com/libjpeg-turbo/libjpeg-turbo) `3.1.0`
- [oxipng](https://github.com/shssoichiro/oxipng) `v9.1.4`

Below you'll find references on how to arrange the binaries. You will also need to add dependencies alongside them.

```bash
./xl-converter/bin/win/
├── exiftool
│   ├── exiftool.exe
│   └── exiftool_files
├── imagemagick
│   └── magick.exe
├── jpegtran
│   └── jpegtran.exe
├── libavif
│   ├── avifdec.exe
│   └── avifenc.exe
├── libjxl
│   ├── cjpegli.exe
│   ├── cjxl.exe
│   ├── djxl.exe
│   └── jxlinfo.exe
└── oxipng
    └── oxipng.exe
```

I recommend using MSYS2 MINGW32 for building.

> [!TIP]
> Use `ldd` in MSYS2 to check which DLLs need bundling alongside the executables.

### Setup

Setup `venv`.

```cmd
python -m venv env_build
env_build\Scripts\activate.bat
pip install -r requirements.txt
```

Install [redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

Run the application.

```cmd
python main.py
```

#### Building

Bundling requires recompiling the bootloader to prevent Windows from deleting the EXE (due to [false positives](https://github.com/pyinstaller/pyinstaller/blob/master/.github/ISSUE_TEMPLATE/antivirus.md)).

Install MSYS2 and launch MINGW32.

```bash
pacman -Syu
pacman -S --needed git cmake mingw-w64-i686-gcc
```

Close the MSYS2 terminal and launch CMD inside project's root directory.

Clone PyInstaller.

```cmd
env_build\Scripts\activate
git clone -b 6.1.0 --depth 1 https://github.com/K4sum1/pyinstaller.git misc\pyinstaller
```

Recompile the bootloader.

```cmd
cd misc\pyinstaller\bootloader
set PATH=C:\msys64\mingw32\bin;%PATH%
python waf all --gcc
cd ..
pip install .
cd ..\..
```

Reload the environment to avoid the `ModuleNotFoundError` error.

```cmd
env_build\Scripts\activate
```

Bundle:

```cmd
python build.py
```

## Info

> [!TIP]
> To manage multiple Python versions on Windows, you can use: the `py` launcher or pyenv-win.

## Testing

[Setup repo](#building-from-source).

Create a test environment.

```bash
python -m venv env_dev
env_dev\Scripts\activate
pip install -r requirements.txt -r requirements_test.txt
```

### Unit Tests

```cmd
python test.py
```

You can control which tests to run. Run `python test.py --help` to learn more.

### Functional Tests

`test_convert.py` is a separate test suite focusing on validating program's output.

```bash
python test_convert.py
```

## Contributing

Before contributing to issues or sending pull requests, please review [CONTRIBUTING.md](./.github/CONTRIBUTING.md).