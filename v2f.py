#!/usr/bin/env python3

import atexit
import os
import signal
import sys

import u2fraw
from u2fhid import U2FHid
from queue import Queue
from channel import mainChannel
from stoppableThread import StoppableThread


PID = os.getpid()
taskQueue = Queue()
hid = U2FHid(taskQueue)

def print_usage_then_exit():
    print('''Usage:
\t%s [<directory>]

The optional directory argument specify the location to store
all information about this virtual U2F authenticator.  The
default value is "~/.v2f".
''' % sys.argv[0])
    sys.exit(1)


def main():
    # # set up SIGINT handler
    def SIGINT_handler(*_, **__):
        print('\nA SIGINT (CTRL-C) signal is detected')
        print("os.close(u2fhid.fd) ")
        t.stop()
        print("t.stop()")
        t1.stop()
        print("t1.stop()")
        reactor.stop()
        # sys.exit(0)
    signal.signal(signal.SIGINT, SIGINT_handler)

    # determine V2F_DIR from argument list
    args = sys.argv[1:]
    if len(args) == 0:
        V2F_DIR = os.path.expanduser('~/.v2f')
    elif len(args) == 1:
        V2F_DIR = args[0]
    else:
        print_usage_then_exit()

    # make sure V2F_DIR is a directory
    os.makedirs(V2F_DIR, exist_ok=True)

    # make sure V2F_DIR/lock does not exist
    try:
        with open(V2F_DIR + '/lock', 'x') as f:
            f.write(str(PID))
    except FileExistsError:
        print('There is already another process using %s to run v2f' % V2F_DIR)
        print('because %s lock file exists' % (V2F_DIR + '/lock'))
        sys.exit(1)

    print('v2f (V2F_DIR=%s PID=%d) started' % (V2F_DIR, PID))

    # remember to clean up
    def clean_up_before_exiting():
        print()
        print('v2f (V2F_DIR=%s PID=%d) ended' % (V2F_DIR, PID))
        os.remove(V2F_DIR + '/lock')
    atexit.register(clean_up_before_exiting)

    # make sure we have V2F_DIR/device_master_secret_key (64-byte)
    # make sure we have V2F_DIR/number_of_signatures_generated (4-byte)
    if not os.path.exists(V2F_DIR + '/device_master_secret_key'):
        with open(V2F_DIR + '/device_master_secret_key', 'wb') as f:
            f.write(os.urandom(64))
    if not os.path.exists(V2F_DIR + '/number_of_signatures_generated'):
        with open(V2F_DIR + '/number_of_signatures_generated', 'wb') as f:
            f.write(b'\x00\x00\x00\x00')

    # read device master secret key
    with open(V2F_DIR + '/device_master_secret_key', 'rb') as f:
        DEVICE_MASTER_SECRET_KEY = f.read()

    # construct a closure that gives you latest counter value
    def update_counter():
        with open(V2F_DIR + '/number_of_signatures_generated', 'rb') as f:
            DEVICE_COUNTER = f.read()
        old_value = int.from_bytes(DEVICE_COUNTER[:4], 'big')
        new_value = old_value + 1
        with open(V2F_DIR + '/number_of_signatures_generated', 'wb') as f:
            f.write(new_value.to_bytes(4, 'big'))
        return old_value

    u2fraw.initialize(DEVICE_MASTER_SECRET_KEY, update_counter, V2F_DIR)

    mainChannel.setObserver(onMessage)

    hid.setup_uhid()
    t = StoppableThread(hidWorker)    
    t.daemon = True
    t.start()
    
    t1 = StoppableThread(infoExchangeWorker)    
    t1.daemon = True
    t1.start()

    # import sys
    from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

    from twisted.python import log
    from twisted.internet import reactor
    from channel import MyServerProtocol

    log.startLogging(sys.stdout)

    print("main task queue:", taskQueue)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    reactor.listenTCP(9000, factory)
    reactor.run()
    # main thread will be block      

import time
def hidWorker(shouldStop):    
    while not shouldStop():    
        time.sleep(1)
        hid.uhid_process_event_from_kernel(shouldStop)
        # print("hidWorker tick")
    
def infoExchangeWorker(shouldStop):
    while not shouldStop():          
        time.sleep(1)
        # print("infoExchangeWorker tick----------")    
        if not taskQueue.empty():
            task = taskQueue.get()
            print("infoExchangeWorker----------")
            print(task.dest)
            print(task.message)
            if task.dest == "HID":                
                hid.send_response_message(task.message)

            elif task.dest == "Channel":
                print(task.message.hex())
                # send to channel
                if mainChannel.isOnline():
                    mainChannel.sendMessage(task.message)                        

import json
from task import HIDTask
# TODO: maybe need to move it to another class
def onMessage(payload, isBinary):    
    print("onMessage===============")
    print(isBinary)    
    print(payload)    

    global taskQueue
        
    t = HIDTask(payload)
    taskQueue.put(t)



if __name__ == '__main__':
    main()
