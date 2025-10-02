from RedisAdapter import RedisAdapter
import threading, time
import argparse
from typing import Optional
import json

# global redis client object
redis = RedisAdapter()

generate_data = False
show_streams = False

def show_streams_thread_function():

    while True and show_streams:
        print('in the thread function')
        streams = redis.get_all_streams()
        print("Streams: ")
        print(streams)
        time.sleep(2)

def blast_injection_redis(entries: int, data: Optional[dict] = None):
    stream_from_config = redis.availableStreams()[0]

    for i in range(1,entries+1):
        
        if data:
            data['id'] = (i+1)
        data = {
            'id': i
        }
        
        # message = json.dumps(data)

        try:
            response = redis.add_entry(stream_from_config, data)
            # print(f"Response received: {response}")
        except Exception as e:
            print('error occurred while adding message to stream')
            print(e)

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--show-streams", action="store_true")
    args = parser.parse_args()

    if args.generate:
        generate_data = True
        
    
    if args.show_streams:
        show_streams = True
        show_streams_thread_ = threading.Thread(target=show_streams_thread_function)
        show_streams_thread_.start()

    if generate_data:
        blast_injection_redis(100)


    

