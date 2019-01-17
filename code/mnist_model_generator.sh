#!/bin/bash
export TFoS_HOME=/home/flaviorissosakakibara/Documents/IGTI/codigo/logparser/data/TensorFlowOnSpark
cd $TFoS_HOME
spark-submit \
--master ${MASTER} \
--py-files ${TFoS_HOME}/examples/mnist/spark/mnist_dist.py \
--conf spark.cores.max=${TOTAL_CORES} \
--conf spark.task.cpus=${CORES_PER_WORKER} \
--conf spark.executorEnv.JAVA_HOME="$JAVA_HOME" \
${TFoS_HOME}/examples/mnist/spark/mnist_spark.py \
--cluster_size ${SPARK_WORKER_INSTANCES} \
--images examples/mnist/csv/train/images \
--labels examples/mnist/csv/train/labels \
--format csv \
--mode train \
--model model/mnist_model

ls -l model/mnist_model
