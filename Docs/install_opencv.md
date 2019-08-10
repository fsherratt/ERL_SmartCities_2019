# Install OpenCV 4.1.1 on Raspbian Buster - RPi4
https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi/
https://www.theimpossiblecode.com/blog/build-faster-opencv-raspberry-pi3/
https://www.reddit.com/r/raspberry_pi/comments/cao24e/faster_opencv_410_for_raspbian_buster/

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

### Install Dependencies
```bash   
$ sudo apt-get install -y \
    devscripts debhelper build-essential \
    ccache unzip pkg-config curl \
    libjpeg-dev libpng-dev \libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libjasper1 libjasper-dev \
    libgtk-3-dev libcanberra-gtk* \
    libatlas-base-dev gfortran \
    libeigen3-dev libtbb-debv \
    python3-dev python3-numpy python2.7-dev python-numpy 
```

### Download OpenCV 4.1.1
```bash
OPENCV_VERSION=4.1.1
cd ~
mkdir opencv
cd opencv

git clone https://github.com/opencv/opencv.git
cd opencv
git checkout tags/${OPENCV_VERSION}
cd ..

git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout tags/${OPENCV_VERSION}
cd ..
```

### Add compiler option
Edit line 326 of `OpenCVCompilerOptions.cmake` in the cmake folder to add the option -latomic

```bash
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OPENCV_EXTRA_FLAGS} ${OPENCV_EXTRA_CXX_FLAGS}")

```
to
```bash
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OPENCV_EXTRA_FLAGS} ${OPENCV_EXTRA_CXX_FLAGS} -latomic")
```

### Build OpenCv for speed
Configure OpenCV with NEON/VFPV3 arguments + redistributable package install. Using TBB, Neon and VFPV3 can result in a 30% improvements in performance

```bash
$ mkdir build
$ cd build
$ cmake ..\
    -D CPACK_BINARY_DEB=ON \
    -D INSTALL_CREATE_DISTRIB=ON \
    -D BUILD_PACKAGE=ON \
    -D BUILD_PACKAGE=ON \
    -D OPENCV_VCSVERSION=${OPENCV_VERSION} \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D ENABLE_PRECOMPILED_HEADERS=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_DOCS=ON \
    -D BUILD_EXAMPLES=OFF \
    -D WITH_TBB=ON \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D WITH_OPENMP=ON \
    -D WITH_EIGEN=ON \
    -D PYTHON3_EXECUTABLE=$(which python3) \
    -D PYTHON_EXECUTABLE=$(which python2)

make -j3

sudo make install
cpack -G DEB
sudo make uninstall
```

### Install
```bash
sudo dpkg -i OpenCV-*.deb
```
