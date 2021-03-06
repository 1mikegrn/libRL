import sys
import socket
from os import path, system

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.split(here)[0])

from libRL.gui.main import run_app

def find_port():
    port_attempts = 0
    while port_attempts < 1000:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 0))
            app_port = sock.getsockname()[1]
            sock.close()
            print('push to port:' + str(app_port))
            return app_port
        except:
            port_attempts += 1


def init():
    port = find_port()
    print('pushing to http://localhost:' + str(port) + '/')
    run_app(port)

if __name__ == "__main__":
    init()
    
# ------------------------------------ devs ------------------------------------

# cef was cool, but we're shelving it until we have more cross-platform 
# integration and 3.8 support

# class handler:
#     def __init__(self):
#         port = find_port()

#         p1 = multiprocessing.Process(target=run_app, args=[port])
#         p2 = multiprocessing.Process(target=self.cef_func, args=[port])

#         p1.start()
#         p2.start()

#         p2.join()
#         p1.terminate()

#     def cef_func(self, port):
        
#         sys.excepthook = cef.ExceptHook
#         cef.DpiAware.EnableHighDpiSupport()

#         cef.Initialize(
#             switches={
#                 'disable-gpu-compositing': None
#             }
#         )
        
#         url = "http://localhost:" + str(port) + '/'

#         cef.CreateBrowserSync(
#             url=url,
#             window_title='libRL.app',
#         )
#         cef.MessageLoop()
#         cef.Shutdown()

#     print("FAILED AFTER 1000 PORT ATTEMPTS")
#     sys.exit(1)

# def browser_version(port):
#     run_app(port)

# def init():

#     if (sys.platform == "win32" and sys.version_info[1] < 8):
#         handler()

#     else:
#         print('Currently the embedded app is available on windows in python 3.7')
#         print('Pushing to localhost...')
#         port = find_port()
#         print('opened on localhost:' + port) 
#         browser_version(port)
