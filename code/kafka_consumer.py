from json import dumps, loads
from kafka import KafkaConsumer
from keras.models import load_model
from keras import Sequential
from time import sleep
import tensorflow as tf
from tensorflow_classification import encodeMessage, loadWordDict, generateTensor


if __name__ == '__main__':

    # Loading keras model and word dictionary
    kerasModelFile = 'model10ep.hdf5'
    wordDictFile = 'word_dictionary.json'
    kerasModel = load_model(kerasModelFile,
                            compile=False,
                            custom_objects={"GlorotUniform": tf.keras.initializers.glorot_uniform}
                            )
    wordDict = loadWordDict(wordDictFile)

    consumer = KafkaConsumer(
        'logs',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        encodedMessage = []
        message = message.value
        hostname = message['host']['name']
        source_file = message['source']
        message = message['message']
        encodedMessage.append(encodeMessage(message, wordDict))
        tensor = generateTensor(encodedMessage)
        prediction = kerasModel.predict(tensor)
        # print('Prediction: ', prediction, ' ', message)
        if prediction < 0.8:
            print("Message readed: ", message,
                  "\n from host: ", hostname,
                  "\n in file: ", source_file)
            print('The encoded message is: ', encodeMessage(message, wordDict))
            print('Predicted Value: ', prediction)
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
