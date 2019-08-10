# Raspbian(RaspberryPi4 Buster) Installation
This is a setup guide for Realsense with RaspberryPi

These steps are for librealsense on the Raspberry Pi4 running raspbian Buster, all packages are the latest releases at time of writing

https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md

### Check versions
```bash
$ uname -a
Linux raspberrypi 4.19.58-v7l+

$ sudo apt-get update; sudo apt-get upgrade
$ sudo reboot
$ uname -a

$ gcc -v
gcc version 8.3.0 (Raspbian 8.3.0-6+rpi1)

$ cmake --version
cmake version x.x.x
```

### Add swap
Initial value is 100MB, but we need to build libraries so initial value isn't enough for that.
In this case, need to switch from 100 to `2048` (2GB).  
```bash
$ sudo nano /etc/dphys-swapfile
CONF_SWAPSIZE=2048

$ sudo /etc/init.d/dphys-swapfile restart swapon -s
```

### Install packages
```bash
$ sudo apt-get install -y libdrm-amdgpu1 libdrm-exynos1 libdrm-freedreno1 libdrm-nouveau2 libdrm-omap1 libdrm-radeon1 libdrm-tegra0 libdrm2

$ sudo apt-get install -y libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2

$ sudo apt install libssl-dev

$ sudo apt-get install -y libdrm-amdgpu1-dbg libdrm-exynos1-dbg libdrm-freedreno1-dbg libdrm-nouveau2-dbg libdrm-omap1-dbg libdrm-radeon1-dbg libdrm-tegra0-dbg libdrm2-dbg

$ sudo apt-get install -y libglu1-mesa libglu1-mesa-dev mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev

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

### update `cmake` version (if cmake is before 3.11.4)
Update to the latest version of cmake, currently 3.15.1
```bash
$ cd ~
$ git clone https://github.com/Kitware/CMake.git
$ cd CMake
$ git checkout tags/v3.15.1
$ ./configure --prefix=/home/pi/CMake
$ ./bootstrap
$ make -j3
$ sudo make install
$ export PATH=/home/pi/CMake/bin:$PATH
$ source ~/.bashrc
$ cmake --version
cmake version 3.15.20190728-g200e
```

### set path
```bash
$ nano ~/.bashrc
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

$ source ~/.bashrc

```

### install `protobuf`
Protobuf is a language and platform netural mechanisms for serialzing data structures.

```bash
$ cd ~
$ git clone https://github.com/google/protobuf.git
$ cd protobuf
$ git checkout tags/v3.9.0
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
```

### install `TBB`
Install TBB (Intel Threading Building Blocks) on rpi is a pain. Thankfully PINTO0309 provides upto date deb files
```bash
$ cd ~
$ wget https://github.com/PINTO0309/TBBonARMv7/raw/master/libtbb-dev_2019U5_armhf.deb
$ sudo dpkg -i ~/libtbb-dev_2019U5_armhf.deb
$ sudo ldconfig
$ rm libtbb-dev_2019U5_armhf.deb
```

### install `OpenCV`
Faster OpenCV 4.1.1 for rpi - based on code produced by dlime, follow instructions here https://github.com/dlime/Faster_OpenCV_4_Raspberry_Pi

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

### Edit CMAKE file to include `libatomic_ops`
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
$ make -j1
$ sudo make install
```

### install pyrealsense2
```bash
$ cd ~/librealsense/build

for python2
$ cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python)

for python3
$ cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)

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
$ sudo -H pip3 install pyopengl_accelerate
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
