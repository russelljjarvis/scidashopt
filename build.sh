#!/bin/bash
git clone -b scidash https://github.com/russelljjarvis/BluePyOpt
git clone -b dev https://github.com/russelljjarvis/neuronunit
wget https://raw.githubusercontent.com/russelljjarvis/scidashopt/master/Dockerfile_spike_server
mv Dockerfile_spike_server Dockerfile
docker build -t scidash/neuronunit-optimization_juypter .
