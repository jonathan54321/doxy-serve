#!/usr/bin/env sh

echo Your container args are: "$@"

if test -d "build"; then
  mv build/_deps _deps
  rm -rf build;
  mkdir -p build
  mv _deps build/_deps
fi

mkdir -p build
cd build
cmake ..
make -j20

./demo
