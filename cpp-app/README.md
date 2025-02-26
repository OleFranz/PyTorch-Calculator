# PyTorch-Calculator C++

### About

My goal is to recreate the Python PyTorch-Calculator app in C++, i never used C++ before so the code might not be good.

### Build

- Get [LibTorch](https://pytorch.org/) (CPU, Release and Debug)
  - Unzip LibTorch Release and Debug
  - Create an environment variable named `LIBTORCH` for the Release version and set its value to the path of the libtorch folder, which contains folders like `lib`, `bin`, `include`, etc.
  - Create an environment variable named `LIBTORCHDEBUG` for the Debug version and set its value to the path of the libtorch debug folder, which contains folders like `lib`, `bin`, `include`, etc.
- Get [OpenCV](https://opencv.org/releases)
  - Install OpenCV
  - Create an environment variable named `OpenCV_DIR` and set its value to the path of the OpenCV folder, which contains folders like `bin`, `x64`, `include`, etc.
  - Add the absolute path of the `/x64/*/bin` folder (where `*` is for example `vc14`, `vc15`, `vc16`, etc.) in the `OpenCV_DIR` to the system PATH
- Get [SFML](https://www.sfml-dev.org/download/)
  - Unzip SFML
  - Create an environment variable named `SFML_DIR` and set its value to the path of the SFML folder, which contains folders like `lib`, `bin`, `include`, etc.
- Get [CMake](https://cmake.org/)
  - Install CMake (select the option to add it to the system PATH)
- Build the app in release mode
  - Open a terminal and cd into the `cpp-app` folder
  - Run ```cmake --preset=x64-release -B build/x64-release && cmake --build build/x64-release --config Release``` to build the app in release mode
  - Run ```.\build\x64-release\Release\cpp-app.exe``` to run the release build
- Build the app in debug mode
  - Run ```cmake --preset=x64-debug -B build/x64-debug && cmake --build build/x64-debug``` to build the app in debug mode
  - Run ```.\build\x64-debug\Debug\cpp-app.exe``` to run the debug build