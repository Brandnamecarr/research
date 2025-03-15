import threading
import time

'''
    Going to simulate a multi-thredded app.

    thread 1: polls for input
                if anything is entered, 'RECV INPUT' will be displayed.
                if q is entered, all threads will terminate
'''
shutting_down = False
input_buffer = ''

# function that runs on the input thread.
def input_thread_function():

    print('input_thread function has spawned.')
    global shutting_down, input_buffer

    while shutting_down is False:
        input_buffer = input('Enter input: \n')
        
        if input_buffer == 'q':
            shutting_down = True
        elif input_buffer == '':
            print('ERROR')
        elif len(input_buffer) > 0:
            print('RECV INPUT')

def processor_thread_function():
    pass

# DRIVER CODE BELOW #
print('Starting thread example:')
input_thread = threading.Thread(target=input_thread_function)
input_thread.start()

processor_thread = threading.Thread(target=processor_thread_function)

while not shutting_down:
    time.sleep(1)


shutting_down = True
input_thread.join()

print(f'Shutting down: {shutting_down} and the input_thread is closed')


