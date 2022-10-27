import sys

from .registry import converts_from_numpy, converts_to_numpy
from sensor_msgs.msg import CompressedImage

import numpy as np
import cv2
from numpy.lib.stride_tricks import as_strided


name_to_dtypes = {
	"rgb8":    (np.uint8,  3),
	"rgba8":   (np.uint8,  4),
	"rgb16":   (np.uint16, 3),
	"rgba16":  (np.uint16, 4),
	"bgr8":    (np.uint8,  3),
	"bgra8":   (np.uint8,  4),
	"bgr16":   (np.uint16, 3),
	"bgra16":  (np.uint16, 4),
	"mono8":   (np.uint8,  1),
	"mono16":  (np.uint16, 1),
	
    # for bayer image (based on cv_bridge.cpp)
	"bayer_rggb8":	(np.uint8,  1),
	"bayer_bggr8":	(np.uint8,  1),
	"bayer_gbrg8":	(np.uint8,  1),
	"bayer_grbg8":	(np.uint8,  1),
	"bayer_rggb16":	(np.uint16, 1),
	"bayer_bggr16":	(np.uint16, 1),
	"bayer_gbrg16":	(np.uint16, 1),
	"bayer_grbg16":	(np.uint16, 1),

    # OpenCV CvMat types 
	"8UC1":    (np.uint8,   1),
	"8UC2":    (np.uint8,   2),
	"8UC3":    (np.uint8,   3),
	"8UC4":    (np.uint8,   4),
	"8SC1":    (np.int8,    1),
	"8SC2":    (np.int8,    2),
	"8SC3":    (np.int8,    3),
	"8SC4":    (np.int8,    4),
	"16UC1":   (np.uint16,   1),
	"16UC2":   (np.uint16,   2),
	"16UC3":   (np.uint16,   3),
	"16UC4":   (np.uint16,   4),
	"16SC1":   (np.int16,  1),
	"16SC2":   (np.int16,  2),
	"16SC3":   (np.int16,  3),
	"16SC4":   (np.int16,  4),
	"32SC1":   (np.int32,   1),
	"32SC2":   (np.int32,   2),
	"32SC3":   (np.int32,   3),
	"32SC4":   (np.int32,   4),
	"32FC1":   (np.float32, 1),
	"32FC2":   (np.float32, 2),
	"32FC3":   (np.float32, 3),
	"32FC4":   (np.float32, 4),
	"64FC1":   (np.float64, 1),
	"64FC2":   (np.float64, 2),
	"64FC3":   (np.float64, 3),
	"64FC4":   (np.float64, 4)
}

dtypes_to_unit = {
    "16UC1":	1e-3,	#[mm]
    "32FC1":	1.0		#[m]
  }

@converts_to_numpy(CompressedImage)
def compressedimage_to_numpy(msg, header_size = 12):
	"""From https://answers.ros.org/question/249775/display-compresseddepth-image-python-cv2/

    Args:
        msg (sensor_msgs.CompressedImage): The ROS CompressedImage message to be converted.
        header_size (int, optional): The size of the message header in bytes. Only needed to decode messages with data format `32FC1`. Defaults to 12.

    Returns:
        np.ndarray: RGB values or depth data expressed in m (depending on msg.format).
    """
	format = msg.format.split(';')
	
	if len(format) == 1:	# if the split has no effect, the CompressedImage is assumed to be RGB
		byte_array = np.frombuffer(msg.data, np.uint8)
		return cv2.imdecode(byte_array, cv2.IMREAD_UNCHANGED)
	
	elif len(format) == 2:	# if the split returns two arguments, the CompressedImage is assumed to be depth
		depth_fmt, compr_type = [arg.strip() for arg in format]
		if compr_type != "compressedDepth":
			raise TypeError("Compression type is expected to be 'compressedDepth'. Instead it is {}".format(compr_type))
		# Remove the header from the raw data
		raw_data = msg.data[header_size:]
		raw_header = msg.data[:header_size]
		img_raw = cv2.imdecode(np.fromstring(raw_data, np.uint8), cv2.IMREAD_UNCHANGED)
		if img_raw is None:   # probably wrong header
			raise ValueError("Could not decode compressed depth image."
							"You may need to change 'header_size'.")
		if depth_fmt == "16UC1":
			data = img_raw
		elif depth_fmt == "32FC1":
			# header: int, float, float
			[__, depthQuantA, depthQuantB] = struct.unpack('iff', raw_header)
			data = depthQuantA / (depth_img_raw.astype(np.float32)-depthQuantB)
			# filter max values
			#data[depth_img_raw == 0] = 0
		else:
			raise TypeError("Deconding of '" + depth_fmt + "' is not implemented.")

		return data * dtypes_to_unit[depth_fmt]	# convert to m
		
	else:
		raise ValueError('msg.format {} cannot be interpreted.'.format(msg.format))


@converts_from_numpy(CompressedImage)
def numpy_to_compressedimage(arr, encoding):
	pass
