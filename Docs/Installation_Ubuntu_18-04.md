# Ubuntu 18.04 Installation of ERL dependencies
Installation of OpenCV, librealsense and simulation enviroment

## Update
```bash
sudo apt update
sudo apt upgrade
```

## Git clone
```bash
git clone https://github.com/fsherratt/ERL_SmartCities_2019.git
cd ERL_SmartCities_2019
```

## Create Virtual Enviroment
```
virtualenv .venv
source .venv/bin/activate

VIRTUAL_ENV=$(pwd)/.venv/
```

## Intel Realsense
Follow instructions https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md

## Install python requirements
```bash
pip install -r requirements.txt
```

## OpenCV 4 install Ubuntu
Install OpenCV 4.1.1 on 18.04

### Dependencies
```bash
$ sudo apt-get install build-essential cmake unzip pkg-config
$ sudo apt-get install libjpeg-dev libpng-dev libtiff-dev
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
$ sudo apt-get install libxvidcore-dev libx264-dev
$ sudo apt-get install libgtk-3-dev
$ sudo apt-get install libatlas-base-dev gfortran
$ sudo apt-get install python3-dev
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

### Install Globally then hack
```bash
$ cmake 
	-D CMAKE_BUILD_TYPE=RELEASE 
	-D CMAKE_INSTALL_PREFIX=/usr/local 
	-D INSTALL_PYTHON_EXAMPLES=ON 
	-D INSTALL_C_EXAMPLES=OFF 
	-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules 
	-D PYTHON_EXECUTABLE=~$(which python3) 
	-D BUILD_EXAMPLES=OFF 
	-D ENABLE_PRECOMPILED_HEADERS=OFF ..
```

Then after install hack into virtual enviroment
```bash
$ cp /usr/local/lib/python3.6/dist-packages/cv* $VIRTUAL_ENV/lib/python3.6/site-packages/ -r
```

### Install directly to venv
```bash
mkdir $VIRTUAL_ENV\local

mkdir build_virtualenv
cd build_virtualenv

cmake   -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/local/ \
	-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
	-D PYTHON3_EXECUTABLE=$VIRTUAL_ENV/bin/python \
	-D PYTHON3_PACKAGES_PATH=$VIRTUAL_ENV/lib/python3.6/site-packages \
	-D PYTHON3_INCLUDE=$VIRTUAL_ENV/include/python3.6m \
	-D PYTHON3_LIBRARY=$VIRTUAL_ENV/lib/python3.6/ \
	-D BUILD_EXAMPLES=OFF \
	-D ENABLE_PRECOMPILED_HEADERS=OFF \
	..
```

### Install
```bash
make -j$(nproc)

sudo make install
sudo ldconfig
```

### Source
https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/
https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313

# Simulation Enviroment
## Get Arducopter
```bash
git clone
cd ardupilot
git checkout tags/Copter-3.6.10
git submodule update --init --recursive
./Tools/scripts/install-prereqs-ubuntu.sh -y
. ~/.profile
```

Log off and on to make permanent

```bash
pip install --upgrade pymavlink MAVProxy --user
```

### Source 
http://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html

## Install JSB Sim
```bash
git clone https://github.com/JSBSim-Team/jsbsim.git jsbsim-code^C
cd jsbsim-code
mkdir build
cd build
cmake ..
make -j4
sudo make install
sudo ldconfig
```





