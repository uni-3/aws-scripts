# coding: utf-8

from __future__ import print_function

import os
import json
import sys
import signal
import traceback

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import flask

import pandas as pd

import tarfile
from gensim.models import KeyedVectors

# model file download under /opt/ml/model
prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model/')


# load model and predict
class SimilarService(object):
    model = None

    @classmethod
    def get_model(cls):
        """
        Get the model object for this instance, loading it if it's not already loaded.
        """
        if cls.model is None:
            # .tar.gz file
            #with tarfile.open(model_path + 'model.tar.gz', 'r:gz') as tf:
            #    tf.extractall(path=model_path)
            cls.model = KeyedVectors.load_word2vec_format(model_path+'vectors.txt', binary=False)

        return cls.model


    @classmethod
    def predict(cls, inputs, topn=5):
        """

        Args:
            inputs(list): list of words for each documents. ex. ['word1', 'word2 word3',...]
            topn: num of words in most_similar words.

        Returns:
            outputs(list): topn of similar words and scores for each words.

        """
        model = cls.get_model()

        outputs = []

        for input in inputs:
            predicts = []

            try:
                results = model.most_similar(positive=input.split(' '), topn=topn)
            except KeyError as e:
                print(e)
                predicts.append({
                    'word': '',
                    'similarity': 0.0
                })
                outputs.append(predicts)
                continue

            for res in results:
                word, sim = res

                predicts.append({
                    'word': word,
                    'similarity': "{:.2f}".format(sim)
                })

            outputs.append(predicts)

        return outputs


# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    # health check
    health = SimilarService.get_model() is not None

    status = 200 if health else 404
    return flask.Response(response='\n', status=status, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'text/csv':
        data = flask.request.data.decode('utf-8')
        s = StringIO(data)

        data = pd.read_csv(s, header=None)

    else:
        return flask.Response(response='This predictor only supports CSV data', status=415, mimetype='text/plain')

    # check custom attributes(arg for topn)
    topn = 5
    try:
        ca = json.loads(flask.request.headers.get('X-Amzn-SageMaker-Custom-Attributes'))
        print('custom attr', ca)

        topn = int(ca['topn']) if ca['topn'] is not None else 5

    except Exception as e:
        print('not set topn custom attribute:', e)

    print('Invoked with {} records'.format(data.shape[0]))

    # Do the prediction
    predictions = SimilarService.predict(list(data[0].astype(str)), topn=topn)

    response = {
        'results': predictions
    }
    out = StringIO()

    # return json
    json.dump(response, out)
    result = out.getvalue()

    # return csv
    #pd.DataFrame(response).to_csv(out, header=False, index=False)
    #result = out.getvalue()


    #return flask.Response(response=result, status=200, mimetype='text/csv')

    return flask.Response(response=result, status=200, mimetype='application/json')
