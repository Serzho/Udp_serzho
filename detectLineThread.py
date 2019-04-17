import threading
import time
import cv2


#поток для обработки кадров
class DetectLineThread(threading.Thread):

    def __init__(self):
        super(DetectLineThread, self).__init__()
        self.daemon = True
        self._stopped = threading.Event() #событие для остановки потока
        self._frame = None #кадр для обработки
        self._newFrameEvent = threading.Event() #событие для контроля поступления кадров
        self.debugFrame = None #визуальный результат работы алгоритма
        self.gain = 128 #чувствительность детектора
        self.direction = 0 #направление движения -1..0..1
        self.lineFound = False #есть ли линия на кадре
        
        
    def run(self):
        print('Frame handler started')
        while not self._stopped.is_set():
            self._newFrameEvent.wait() #ждем появления нового кадра
            if not (self._frame is None): #если получен кадр
                #time.sleep(0.5) #имитируем обработку кадра
                self.detectLine()
                self.debugFrame = self._frame
                
            self._newFrameEvent.clear() #сбрасываем событие
            
        print('Frame handler stopped')

    def stop(self):
        self._stopped.set()
        if self.isReady(): #если кадр не обрабатывается
            self._frame = None
            self._newFrameEvent.set() 
        self.join() #ждем завершения работы потока

    def setFrame(self, frame): #задание нового кадра для обработки
        if not self._newFrameEvent.is_set(): #если обработчик готов принять новый кадр
            self._frame = frame
            self._newFrameEvent.set() #задали событие
            return True
        return False

    def isReady(self): #готовность обработать кадр
        return not self._newFrameEvent.is_set()


    def gainDown(self):
        if self.gain > 0:
            self.gain -= 1

    def gainDown(self):
        if self.gain < 255:
            self.gain += 1
            
    def detectLine(self):
        
        self.direction = 0 #направление движения
        self.lineFound = False

        #преобразуем в градации серого
        gray = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
        
        #размываем изображение
        blur = cv2.GaussianBlur(gray, (5, 5), 2)

        #бинаризация в ч/б (исходное изобр, порог, максимальное знач.,
        #тип бинаризации)
        _, thresh = cv2.threshold(blur, self.gain, 255,
                                  cv2.THRESH_BINARY_INV)
        
        #находим контуры
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            
            #отрисовываем контур на исходной картинке
            cv2.drawContours(self._frame, contours, -1,
                            (0, 255, 0), 3, cv2.FILLED) #отображаем контуры на изображении
        
            
