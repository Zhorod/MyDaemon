import cv2
import numpy as np
import tarfile
import urllib.request
import os
import datetime
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
import six
from six.moves import range
from six.moves import zip

class ObjectDetector():
  def __init__(self):

    # check the directory structure exists
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    MODELS_DIR = os.path.join(DATA_DIR, 'models')
    for dir in [DATA_DIR, MODELS_DIR]:
      if not os.path.exists(dir):
        os.mkdir(dir)

    # Download and extract model
    MODEL_DATE = '20200711'
    MODEL_NAME = 'ssd_resnet101_v1_fpn_640x640_coco17_tpu-8'
    MODEL_TAR_FILENAME = MODEL_NAME + '.tar.gz'
    MODELS_DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/tf2/'
    MODEL_DOWNLOAD_LINK = MODELS_DOWNLOAD_BASE + MODEL_DATE + '/' + MODEL_TAR_FILENAME
    PATH_TO_MODEL_TAR = os.path.join(MODELS_DIR, MODEL_TAR_FILENAME)
    PATH_TO_CKPT = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, 'checkpoint/'))
    PATH_TO_CFG = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, 'pipeline.config'))
    if not os.path.exists(PATH_TO_CKPT):
      print('Downloading model. This may take a while... ', end='')
      urllib.request.urlretrieve(MODEL_DOWNLOAD_LINK, PATH_TO_MODEL_TAR)
      tar_file = tarfile.open(PATH_TO_MODEL_TAR)
      tar_file.extractall(MODELS_DIR)
      tar_file.close()
      os.remove(PATH_TO_MODEL_TAR)
      print('Done')

    # Download labels file
    LABEL_FILENAME = 'mscoco_label_map.pbtxt'
    LABELS_DOWNLOAD_BASE = \
      'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/'
    PATH_TO_LABELS = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, LABEL_FILENAME))
    if not os.path.exists(PATH_TO_LABELS):
      print('Downloading label file... ', end='')
      urllib.request.urlretrieve(LABELS_DOWNLOAD_BASE + LABEL_FILENAME, PATH_TO_LABELS)
      print('Done')

    # Next we load the downloaded model

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  # Suppress TensorFlow logging
    # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow logging (2)

    # Enable GPU dynamic memory allocation
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)

    print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

    # Load pipeline config and build a detection model
    self.configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
    self.model_config = self.configs['model']
    self.detection_model = model_builder.build(model_config=self.model_config, is_training=False)

    # Restore checkpoint
    self.ckpt = tf.compat.v2.train.Checkpoint(model=self.detection_model)
    self.ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-0')).expect_partial()

    self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
    print("Initiated object detector class")

  def detect_fn(self, image):
    """Detect objects in image."""
    image, shapes = self.detection_model.preprocess(image)
    prediction_dict = self.detection_model.predict(image, shapes)
    detections = self.detection_model.postprocess(prediction_dict, shapes)
    return detections, prediction_dict, tf.reshape(shapes, [-1])

  def get_date_time(self):
    # create a time stamp
    now = datetime.datetime.now()
    dt_string = now.strftime("%Y") + "-" + now.strftime("%b") + "-" + now.strftime("%d") + "-" + now.strftime(
      "%H") + "-" + now.strftime("%M") + "-" + now.strftime("%S")
    return(dt_string)

  # process an image
  def process_image(self, image_np):

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections, predictions_dict, shapes = self.detect_fn(input_tensor)

    # check to see if there are any detections
    # if there are, save the image and the detections

    # have there been any detections

    # is there something interesting
    interesting = True

    if interesting and detections:

      # show the image with detections
      # take a copy of the image to add the detection boxes

      # not sure what this is for
      label_id_offset = 1

      # copy the image
      image_np_with_detections = image_np.copy()

      # add the detection boxes
      viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,

        detections['detection_boxes'][0].numpy(),
        (detections['detection_classes'][0].numpy() + label_id_offset).astype(int),
        detections['detection_scores'][0].numpy(),
        self.category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.30,
        agnostic_mode=False)

      # Display output
      cv2.imshow('object detection', cv2.resize(image_np_with_detections, (800, 600)))
      cv2.waitKey(25)

      # save the image
      #filename = "C:/Local/temp/mdti-" + self.get_date_time() + "-raw.jpg"
      #result = cv2.imwrite(filename, cv2.resize(image_np, (800, 600)))
      #if result == True:
      #  print("File saved successfully")
      #else:
      #  print("Error in saving file")

      # save the detection data

      # print the category index

      # lets decode the first detection
      boxes = detections['detection_boxes'][0].numpy()
      classes = (detections['detection_classes'][0].numpy() + label_id_offset).astype(int)
      scores = detections['detection_scores'][0].numpy()

      min_score_thresh = 0.5

      for i in range(boxes.shape[0]):
        if scores is None or scores[i] > min_score_thresh:
          print("score: ", scores[i])
          box = tuple(boxes[i].tolist())
          print("box: ", box)
          if classes[i] in six.viewkeys(self.category_index):
            class_name = self.category_index[classes[i]]['name']
          else:
            class_name = 'N/A'
          display_str = str(class_name)
          print("Class: ", display_str)

      #print(self.category_index)

      #for box in detections['detection_boxes']:
      #  print(box.numpy())
      #for detection_class in detections['detection_classes']:
      #  print(detection_class.numpy())
      #for score in detections['detection_scores']:
      #  print(score.numpy())

    print("processed an image")

