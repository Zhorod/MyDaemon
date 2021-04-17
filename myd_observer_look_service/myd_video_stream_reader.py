import cv2, queue, threading, time

# bufferless VideoCapture
# threaded

class VideoStreamReader:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    # gets the latest frame
    return self.q.get()

#cap = VideoStreamReader(0)
#while True:
#  time.sleep(.5)   # simulate time between events
#  frame = cap.read()
#  cv2.imshow("frame", frame)
#  if chr(cv2.waitKey(1)&255) == 'q':
#    break