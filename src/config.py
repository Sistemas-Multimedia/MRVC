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
#lowest_Q_step = 21
#highest_Q_step = 42
#step_Q_step = 3

# DCT
lowest_Q_step = 4
highest_Q_step = 32
step_Q_step = 4

#temporal_codec = "image_IPP"
#temporal_codec = "image_IPP_adaptive"
temporal_codec = "MP4"
