#!/usr/bin/env python3
# Fridosleigh.com CAPTEHA API - Made by Krampus Hollyfeld
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)
import requests
import json
import sys
import numpy as np
import threading
import queue
import time
import csv


device_name = tf.test.gpu_device_name()
print('---')
print(device_name)
print('---')

exit()
# sudo apt install python3-pip
# sudo python3 -m pip install --upgrade pip
# sudo python3 -m pip install --upgrade setuptools
# sudo python3 -m pip install --upgrade tensorflow==1.15

def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label

def predict_image(q, sess, graph, image_bytes, hash_key, uuid, labels, input_operation, output_operation):
    image = read_tensor_from_image_bytes(image_bytes)
    results = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: image
    })
    results = np.squeeze(results)
    prediction = results.argsort()[-5:][::-1][0]
    q.put( {'uuid':uuid, 'prediction':labels[prediction].title(), 'percent':results[prediction], 'hash_key':hash_key} )

def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()
    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)
    return graph

def read_tensor_from_image_bytes(imagebytes, input_height=299, input_width=299, input_mean=0, input_std=255):
    image_reader = tf.image.decode_png( imagebytes, channels=3, name="png_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.compat.v1.Session()
    result = sess.run(normalized)
    return result

def load_guesses_dictionary():
    with open('guesses.csv', mode='r') as infile:
        reader = csv.reader(infile)
        guesses = {rows[0]:rows[1] for rows in reader}
        print(len(guesses))
        return guesses

def main():
    '''
    LOADING
    '''
    guesses = {}
    try:
        guesses = load_guesses_dictionary()
    except:
        pass

    #This list should contains only uuids predicted by our ML model to match the challenge_image_type
    b64_images_match = []
    
    # Loading the Trained Machine Learning Model created from running retrain.py on the training_images directory
    graph = load_graph('/tmp/retrain_tmp/output_graph.pb')
    labels = load_labels("/tmp/retrain_tmp/output_labels.txt")

    # Load up our session
    input_operation = graph.get_operation_by_name("import/Placeholder")
    output_operation = graph.get_operation_by_name("import/final_result")
    sess = tf.compat.v1.Session(graph=graph)

    # Can use queues and threading to spead up the processing
    q = queue.Queue()



    '''
    REQUESTING
    '''
    yourREALemailAddress = "AAAAAAYourRealEmail@SomeRealEmailDomain.RealTLD"

    # Creating a session to handle cookies
    s = requests.Session()
    url = "https://fridosleigh.com/"

    json_resp = json.loads(s.get("{}api/capteha/request".format(url)).text)
    b64_images = json_resp['images']                    # A list of dictionaries eaching containing the keys 'base64' and 'uuid'
    challenge_image_type = json_resp['select_type'].split(',')     # The Image types the CAPTEHA Challenge is looking for.
    challenge_image_types = [challenge_image_type[0].strip(), challenge_image_type[1].strip(), challenge_image_type[2].replace(' and ','').strip()] # cleaning and formatting

    '''
    MISSING IMAGE PROCESSING AND ML IMAGE PREDICTION CODE GOES HERE
    '''
    import base64

    #challenge_image_types = [i.replace(' ','_') for i in challenge_image_types]

    queue_size = len(b64_images)
    for img in b64_images:
        #convert base64 representation of image into bytes
        hash_key = hash(img['base64'])
        uuid = img['uuid']
        if str(hash_key) in guesses.keys():
            queue_size -= 1
            if guesses[str(hash_key)] in challenge_image_types:
                print("Found image from csv cache")
                b64_images_match.append(uuid)
        else:
            image_bytes = base64.b64decode(img['base64'])
            #Classify the image type using our ML Image recognition model
            threading.Thread(target=predict_image, args=(q, sess, graph, image_bytes, str(hash_key), uuid, labels, input_operation, output_operation)).start()

    print('Waiting For Threads to Finish...')
    while q.qsize() < queue_size:
       time.sleep(0.001)

    #getting a list of all threads returned results
    prediction_results = [q.get() for x in range(q.qsize())]

    #do something with our results... Like print them to the screen.
    for prediction in prediction_results:
        print('TensorFlow Predicted {uuid} is a {prediction} with {percent:.2%} Accuracy'.format(**prediction))
        img_type = '{prediction}'.format(**prediction)
        if img_type in challenge_image_types:
            b64_images_match.append('{uuid}'.format(**prediction))

    # This should be JUST a csv list image uuids ML predicted to match the challenge_image_type .
    #final_answer = ','.join( [ img['uuid'] for img in b64_images_match ] )
    final_answer = ','.join(b64_images_match)

    #print(final_answer)
    
    '''
    END OF CUSTOM CODE
    '''
    
    json_resp = json.loads(s.post("{}api/capteha/submit".format(url), data={'answer':final_answer}).text)
    if not json_resp['request']:
        # If it fails just run again. ML might get one wrong occasionally
        print('FAILED MACHINE LEARNING GUESS')
        print('--------------------\nOur ML Guess:\n--------------------\n{}'.format(final_answer))
        print('--------------------\nServer Response:\n--------------------\n{}'.format(json_resp['data']))
        #Save our guesses in a CSV file
        for prediction in prediction_results:
            hash_key = '{hash_key}'.format(**prediction) #.split('-')[0]
            label = '{prediction}'.format(**prediction)
            guesses[str(hash_key)]=label
        with open('guesses.csv', 'w') as f:
            for key in guesses.keys():
                f.write("%s,%s\n"%(key,guesses[str(key)]))
        sys.exit(1)

    print('CAPTEHA Solved!')
    # If we get to here, we are successful and can submit a bunch of entries till we win
    userinfo = {
        'name':'Krampus Hollyfeld',
        'email':yourREALemailAddress,
        'age':180,
        'about':"Cause they're so flippin yummy!",
        'favorites':'thickmints'
    }
    # If we win the once-per minute drawing, it will tell us we were emailed. 
    # Should be no more than 200 times before we win. If more, somethings wrong.
    entry_response = ''
    entry_count = 1
    while yourREALemailAddress not in entry_response and entry_count < 200:
        print('Submitting lots of entries until we win the contest! Entry #{}'.format(entry_count))
        entry_response = s.post("{}api/entry".format(url), data=userinfo).text
        entry_count += 1
    print(entry_response)


if __name__ == "__main__":
    main()
