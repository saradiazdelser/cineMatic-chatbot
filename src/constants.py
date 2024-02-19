params={
    'generate_max_length': 300,
    'no_repeat_ngram_size': 0,
    'sampling_topk': 50,
    'sampling_topp': 0.95,
    'sampling_temperature': 0.3,
    'repetition_penalty': 1.0
    }

API_HOST = '10.182.1.48'
API_PORT = '8080'
stream_url = "http://{}:{}/generate_stream".format(API_HOST,API_PORT)
generate_url = "http://{}:{}/generate".format(API_HOST,API_PORT)
base_url = "http://{}:{}".format(API_HOST,API_PORT)