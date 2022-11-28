import time
import os
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

buttonfileStr = 'buttonfile = buttons.cfg\n'
defaultButton = """type = extension
context = MyContext
label = Operator
"""


def editFop2Cfg():
    secret = ''
    fop2ConfigContents = ''
    buttonContents = ''
    gFile = open('AMI.conf', 'r')
    gContents = gFile.read()+'\n\n'
    gFile.close()
    file = open('/mnt/fop2/asterisk/sip.conf', 'r')
    contents = file.read()
    file.close()
    isLabel = False
    ext = ''
    para = ''
    tmp = ''
    for x in contents:
        if x == '[':
            isLabel = True
        elif isLabel is True and x != ']':
            tmp += x
        elif x == ']':
            isLabel = False
            if (tmp.isdigit()):
                ext = tmp
            tmp = ''
        elif isLabel is False:
            para += x
            if x == '\n':
                para = para[0:len(para)-1]
                para = para.replace(" ", "")
                if para.__contains__('secret='):
                    if len(para.split('=')) > 1:
                        secret = para.split('=')[1]
                        fop2ConfigContents += 'user='+ext+':'+secret+':all\n'+buttonfileStr
                        label = '[SIP/'+ext+']\n'
                        extension = 'extension='+ext+'\n'
                        buttonContents += label+extension+defaultButton
                para = ''

    file = open('/usr/local/fop2/fop2.cfg', 'w')
    fop2ConfigContents = gContents+fop2ConfigContents
    file.write(fop2ConfigContents)
    file.close()
    file = open('/usr/local/fop2/buttons.cfg', 'w')
    file.write(buttonContents)
    file.close()


class MyHandler(FileSystemEventHandler):
    def on_modified(self,  event):
        print(f'event type: {event.event_type} path : {event.src_path}')
        if (event.src_path.__contains__('sip.conf')):
            editFop2Cfg()
            os.system('sudo /etc/init.d/fop2 restart')


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = PollingObserver()
    observer.schedule(
        event_handler, path='/mnt/fop2/asterisk/', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
