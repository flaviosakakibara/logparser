#!/bin/bash

export TFoS_HOME=/home/flaviorissosakakibara/Documents/IGTI/codigo/logparser/data/TensorFlowOnSpark
cd ${TFoS_HOME}
mkdir -p examples/mnist/csv
rm -rf examples/mnist/csv/*
spark-submit --master ${MASTER} ${TFoS_HOME}/examples/mnist/mnist_data_setup.py --output examples/mnist/csv --format csv
ls -lR examples/mnist/csv
