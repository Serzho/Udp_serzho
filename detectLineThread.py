import threading
import cv2
import time

#поток для обработки кадров
class DetectLineThread(threading.Thread):
    def __init__(self):
        super(DetectLineThread, self).__init__()
        self.daemon = True
        self._stopped = threading.Event()
        self._frame = None #Кадр
        self._newFrameEvent = threading.Event() 
        self.debugFrame = None #Визуальный кадр
        
    def run(self):
        print('Frame handler started')
        while not self._stopped.is_set():
            self._newFrameEvent.wait() #Ждем получения нового кадра
            if not (self._frame is None): #Если получен кадр               
                time.sleep(0.01)
                #Обработка кадра
                self.debugFrame = cv2.GaussianBlur(self._frame, (5, 5), 2)
                '''
                if not self.debugFrame is None:
                    print('OK!!!')
                else:
                    print('Ow(((')
                '''
            self._newFrameEvent.clear() #Сбрасываем событие
        print('Frame handler stopped')

    def stop(self):
        self._stopped.set()
        if self.isReady:
            self._frame = None
            self._newFrameEvent.set()
        self.join() #Дождаться завершения потока

    def setFrame(self, frame):
        if self.isReady():
            self._frame = frame
            self._newFrameEvent.set()
            return True
        return False

    def isReady(self): #Готов ли получать новый кадр
        return not self._newFrameEvent.set()
