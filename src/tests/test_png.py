import cv2
import numpy as np
import tempfile as tf

image = (np.random.rand(256, 256) * 255).astype('uint16')
tmp = tf.NamedTemporaryFile(suffix='.png', prefix='a')
tmp.close()
print(tf.gettempdir())
cv2.imwrite(tmp.name, image)
image2 = cv2.imread(tmp.name, -1)
print((image == image2).all())
print(type(image[0][0]))
print(type(image2[0][0]))

image = (np.random.rand(256, 256) * 255).astype('int16')
cv2.imwrite(tmp.name, image)
image2 = cv2.imread(tmp.name, -1)
print((image == image2).all())
print(type(image[0][0]))
print(type(image2[0][0]))

