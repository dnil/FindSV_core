cd $1
git clone https://github.com/J35P312/FindTranslocations.git
cd FindTranslocations
mkdir build
cd build
cmake ..  -DBoost_NO_BOOST_CMAKE=ON
make
