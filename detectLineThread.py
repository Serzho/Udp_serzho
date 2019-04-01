import threading
import cv2

#поток для обработки кадров
class DetectLineThread(threading.Thread):
    def __init__(self):
        super(DetectLineThread, self).__init__()
        self.daemon = True
        self._stopped = threading.Event()
        self._frame = None
        self._newFrameEvent = threading.Event()
        
    def run(self):
        print('Frame handler started')
        while not self._stopped.is_set():
            self._newFrameEvent.wait() #Ждем получения нового кадра
            if not (self._frame is None): #Если получен кадр               
                time.sleep(1) 
                #Обработка кадра
            self._newFrameEvent.clear() #Сбрасываем событие
        print('Frame handler stopped')

    def stop(self):
        self._stopped.set()
        if not self._newFrameEvent.is_set():
            self._frame = None
            self._newFrameEvent.set()
        self.join() #Дождаться завершения потока

    def setFrame(self, frame):
        if not self._newFrameEvent.is_set():
            self._frame = frame
            self._newFrameEvent.set()
            return True
        return False
