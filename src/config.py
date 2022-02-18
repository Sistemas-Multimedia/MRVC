''' MRVC/config.py

Experiment configuration.
'''

#multiresolution_transform = "DWT"
#multiresolution_transform = "LP"
multiresolution_transform = None

#spatial_codec = "Q+PNG"
#spatial_codec = "H264"
spatial_codec = "DCT"

color = "YCoCg"
#color = "YCrCb"
#color = "RGB"

#quantizer = "H264"
#quantizer = "deadzone"

# H264
#Q_steps = range(42, 41, -3)
#Q_steps = range(42, 21, -3)
Q_steps = range(21, 42, 3)


# DCT
#Q_steps = [32]
#Q_steps = [128, 64, 32, 16, 8]
#Q_steps = [8, 16, 32, 64, 128]

#temporal_codec = "image_IPP"
#temporal_codec = "image_IPP_adaptive"
temporal_codec = "MP4"
