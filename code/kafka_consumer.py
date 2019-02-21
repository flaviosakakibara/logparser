from json import dumps, loads
from kafka import KafkaConsumer
from keras.models import load_model
from keras import Sequential
from time import sleep
import tensorflow as tf
from tensorflow_classification import encodeMessage, loadWordDict, generateTensor


if __name__ == '__main__':

    priorities = [
        'emerg',
        'alert',
        'crit',
        'err',
        'warning',
        'notice',
        'info',
        'debug'
    ]
    consumers = {}
    for priority in priorities:
        kConsumer = KafkaConsumer(
            priority,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        consumers[str(priority)] = kConsumer

    # Loading keras model and word dictionary
    kerasModelFile = 'dataset_tail-20.hdf5'
    wordDictFile = 'dataset_tail.dict.json'
    kerasModel = load_model(kerasModelFile,
                            compile=False,
                            custom_objects={"GlorotUniform": tf.keras.initializers.glorot_uniform}
                            )
    wordDict = loadWordDict(wordDictFile)

    evaluatedPriority = 'emerg'
    messageTotal = 0
    for message in consumers[str(evaluatedPriority)]:
        encodedMessage = []
        # Parsing message readed on pipe
        message = message.value
        hostname = message['host']['name']
        source_file = message['source']
        message = message['message']

        # Encoding message for model application
        encodedMessage.append(encodeMessage(message, wordDict))
        tensor = generateTensor(encodedMessage)
        prediction = kerasModel.predict_classes(tensor)

        print((prediction))


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
