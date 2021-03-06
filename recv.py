from __future__ import print_function
import socket
from contextlib import closing
import pyaudio
import wave
import datetime
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 8
RATE = 16000
RECORD_SECONDS = 7200

def main():
    local_address = '192.168.12.3'
    multicast_group = '239.255.0.1'
    port = 4000
    bufsize = 4096

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(multicast_group) + socket.inet_aton(local_address))
        message = sock.recv(bufsize)
        start = time.time()
        for j in range(0, 4):
            d = datetime.datetime.today().strftime("%Y%m%d-%H%M%S")
            WAVE_OUTPUT_FILENAME = "/media/pi/BC02-7EB4/TAMAGO3_{0}.wav".format(d)
            
            p = pyaudio.PyAudio()
            
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            print("* recording")
            
            cnt = 0
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                cnt += 1
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                if cnt % 9000 == 0:
                    wf.writeframes(b''.join(frames))
                    frames = []
                
            print("* done recording (cnt = {0})".format(cnt))
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            wf.close()

        while True:
            message = sock.recv(bufsize)
            if message == 'stop':
                break
    
    finish = time.time()
    print("elapsed_time:{0}".format(finish - start) + "[sec]")
    
    return

if __name__ == '__main__':
    main()

