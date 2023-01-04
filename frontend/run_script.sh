#!/bin/sh

cd /frontend

echo "install node modules"
npm install -f --no-optional --global webpack webpack-cli
npm install -f --no-optional

echo "start build"

if [ "$1" = "build" ]; then
  echo "Production"
  webpack --mode production -o /frontend/dist
elif [ "$1" = "dev" ]; then
  echo "Development"
  webpack --watch --mode development -o /frontend/dist
fi

echo "build completed"
