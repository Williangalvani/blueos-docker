gst-launch-1.0 udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! queue ! autovideosink