from json import dumps, loads
from kafka import KafkaConsumer
from keras.models import load_model
from time import sleep


if __name__ == '__main__':

    kerasModelFile = 'model10ep.hdf5'

    kerasModel = load_model(kerasModelFile, compile=False)
    consumer = KafkaConsumer(
        'logs',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value
        hostname = message['host']['name']
        source_file = message['source']
        message = message['message']
        print("Li a mensagem: ", message,
              "\n do host: ", hostname,
              "\n no arquivo: ", source_file)
    '''
    Exemplo de output
    {
        '@timestamp': '2019-01-22T18:58:13.268Z',
        '@metadata':
        {
            'beat': 'filebeat',
            'type': 'doc',
            'version': '6.4.2',
            'topic': 'logs'
        },
        'input':
        {
            'type': 'log'
        },
        'beat':
        {
            'name': 'saka-pc',
            'hostname': 'saka-pc',
            'version': '6.4.2'
        },
        'host':
        {
            'name': 'saka-pc'
        },
        'source': '/var/log/teste/gluster.log',
        'offset': 3864,
        'message': '[ 19.568] (==) Matched nv as autoconfigured driver2',
        'prospector': {'type': 'log'}
    }
    '''
