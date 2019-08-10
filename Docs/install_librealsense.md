# Librealsense Installation on Raspbian Buster - RPi4
These steps are for librealsense on the Raspberry Pi4 running raspbian Buster. Based on https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md

### Make sure everything is up to date
```bash
$ sudo apt-get purge -y libreoffice*
$ sudo apt-get clean
$ sudo apt-get update
$ sudo apt-get upgrade -y
$ sudo apt-get dist-upgrade -y
$ sudo apt-get autoremove -y

$ sudo pip2 install -U pip
$ sudo pip3 install -U pip
```

### Install packages
```bash
$ sudo apt install -y libdrm-amdgpu1 libdrm-exynos1 libdrm-freedreno1 libdrm-nouveau2 libdrm-omap1 libdrm-radeon1 libdrm-tegra0 libdrm2

$ sudo apt install -y libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2

$ sudo apt install libssl-dev

$ sudo apt install -y libglu1-mesa libglu1-mesa-dev mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev
```

### update udev rule
Now we need to get librealsense from the repo(https://github.com/IntelRealSense/librealsense). v2.23.0 is latest stable release
```bash
$ cd ~
$ git clone https://github.com/IntelRealSense/librealsense.git
$ cd librealsense
$ git checkout tags/v2.23.0
$ sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/ 
$ sudo udevadm control --reload-rules && sudo udevadm trigger 
```

### install `OpenCV`
Follow (Docs/install_opencv.md)[https://github.com/fsherratt/ERL_SmartCities_2019/blob/sim/Docs/install_opencv.md] 

### install `protobuf`
Protobuf is a language and platform netural mechanisms for serialzing data structures. v3.5.1 is recommended version although not the latest

```bash
$ cd ~
$ git clone https://github.com/google/protobuf.git
$ cd protobuf
$ git checkout tags/v3.9.1
$ ./autogen.sh
$ ./configure
$ make -j3
$ sudo make install
```

Link to python
```
$ cd python
$ export LD_LIBRARY_PATH=../src/.libs
$ python3 setup.py build --cpp_implementation 
$ python3 setup.py test --cpp_implementation
$ sudo python3 setup.py install --cpp_implementation
$ export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
$ export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=3
$ sudo ldconfig
$ protoc --version
libprotoc 3.9.1
```

### install `libatomic_ops`  atomic_ops library
Don't know if this step is required
```bash
git clone https://github.com/ivmai/libatomic_ops.git
cd libatomic_ops
git checkout tags/v7.6.10
./autogen.sh
./configure
make -j3
sudo make install
```

### Edit CMAKE file to include `libatomic_ops`\
https://github.com/IntelRealSense/librealsense/issues/4375

edit file `CMake/unix_config.cmake` linke 11 and add `-latomic` to the `CMAKE_CXX_FLAGS`
from
```bash
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mfpu=neon -mfloat-abi=hard -ftree-vectorize")
```
to 
```bash
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mfpu=neon -mfloat-abi=hard -ftree-vectorize -latomic")
```


### install `RealSense` SDK/librealsense
Now for the main event
```bash
$ cd ~/librealsense
$ mkdir  build  && cd build
$ cmake .. -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true 
$ make -j3
$ sudo make install
```

### install pyrealsense2
```bash
$ cd ~/librealsense/build

for python2
$ cmake ..  -DBUILD_EXAMPLES=false -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python)

for python3
$ cmake ..  -DBUILD_EXAMPLES=false -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)

$ make -j1
$ sudo make install

add python path
```bash
$ nano ~/.bashrc
export PYTHONPATH=$PYTHONPATH:/usr/local/lib

$ source ~/.bashrc
```

### change `pi` settings (enable OpenGL)
```bash
$ sudo apt-get install python-opengl
$ sudo -H pip3 install pyopengl
$ sudo raspi-config
"7.Advanced Options" - "A7 GL Driver" - "G2 GL (Fake KMS)"
```

Finally, need to reboot pi
```bash
$ sudo reboot
```


### Try RealSense
Connected a camera to the pi and run
```bash
$ realsense-viewer
```
