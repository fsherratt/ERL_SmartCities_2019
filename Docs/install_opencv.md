# Install OpenCV 4.1.1 on Raspbian Buster - RPi4
Based on the following
https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi/
https://www.theimpossiblecode.com/blog/build-faster-opencv-raspberry-pi3/
https://www.reddit.com/r/raspberry_pi/comments/cao24e/faster_opencv_410_for_raspbian_buster/
https://gist.github.com/willprice/abe456f5f74aa95d7e0bb81d5a710b60

### Make sure everything is up to date
```bash
$ sudo apt-get purge -y libreoffice*
$ sudo apt-get clean
$ sudo apt-get update
$ sudo apt-get upgrade -y
$ sudo apt-get dist-upgrade -y
$ sudo apt-get autoremove -y

$ sudo pip3 install -U pip
```

### Add swap
Initial value is 100MB, but we need to build libraries so initial value isn't enough for that.
In this case, need to switch from 100 to `2048` (2GB).  
```bash
$ sudo nano /etc/dphys-swapfile
CONF_SWAPSIZE=2048

$ sudo /etc/init.d/dphys-swapfile restart swapon -s
```

### Install Dependencies
```bash
$ sudo apt install -y devscripts debhelper libldap2-dev libgtkmm-3.0-dev libarchive-dev \
    libcurl4-openssl-dev opencl-headers
$ sudo apt install -y build-essential pkg-config gfortran cmake libjpeg-dev libtiff5-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev \
    libatlas-base-dev libblas-dev libeigen3-dev liblapack-dev \
    python3-dev python3-numpy
```

### set path
```bash
$ nano ~/.bashrc
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

$ source ~/.bashrc
```

### Download OpenCV 4.5.5
```bash
OPENCV_VERSION=4.5.5
cd ~
mkdir opencv
cd opencv

git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout tags/${OPENCV_VERSION}
cd ..

git clone https://github.com/opencv/opencv.git
cd opencv
git checkout tags/${OPENCV_VERSION}
cd ..
```

### Build OpenCv for speed
Configure OpenCV with NEON VFPV3 arguments + redistributable package install. Using TBB, Neon and VFPV3 can result in a 30% improvements in performance

```bash
$ mkdir build
$ cd build
$ cmake ..\
    -D INSTALL_CREATE_DISTRIB=ON \
    -D BUILD_PACKAGE=ON \
    -D OPENCV_VCSVERSION=${OPENCV_VERSION} \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH= ~/opencv/opencv_contrib/modules \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_DOCS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D ENABLE_PRECOMPILED_HEADERS=OFF \
    -D WITH_TBB=ON \
    -D BUILD_TBB=ON \
    -D WITH_OPENMP=ON \
    -D ENABLE_NEON=ON \
    -D OPENCV_EXTRA_EXE_LINKER_FLAGS=-latomic \
    -D PYTHON3_EXECUTABLE=$(which python3)

make -j3

sudo make install
cpack -G DEB
sudo make uninstall
```

### Install
```bash
sudo dpkg -i OpenCV-*.deb
```
