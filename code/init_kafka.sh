#!/bin/bash

kafka_home=/opt/kafka/kafka_2.12-0.11.0.3
base_dir=$(dirname $0)

input_file=$1
output_file=/var/log/teste/gluster.log

export JAVA_HOME=/usr/java/jdk1.8.0_191-amd64

if [ -z $input_file ]
then
   echo "Informe o arquivo de log a ser consumido"
   exit 3
fi 

if [ ! $(pgrep filebeat) ]
then
   echo "Filebeat não está rodando"
   exit 1
fi

$kafka_home/bin/zookeeper-server-start.sh -daemon $kafka_home/config/zookeeper.properties
$kafka_home/bin/kafka-server-start.sh $kafka_home/config/server.properties  >> $base_dir/kafka-server.log &

if [ $(ss -ntlp | grep 2181) ]
then
   echo "kafka não subiu corretamente"
   exit 2
fi

echo "Iniciando gerador de logs"
./gerador_logs.sh $input_file $output_file &

while true
do
	clear
	echo "Realizando a geração de log..."
    echo "Deseja encerrar a execução?[s/S/n/N]"
	read user_input
	case $user_input in 
	   	's')
			break;;
		'S')
			break;;
		'n')
			continue;;
		'N')
			continue;;
		*)
			echo "Valor incorreto"
			continue;;
	esac
done

echo "Encerrando processos"
$kafka_home/bin/kafka-server-stop.sh
$kafka_home/bin/zookeeper-server-stop.sh
echo "Limpando arquivo de log"
rm -r $output_file
rm $base_dir/kafka-server.log

