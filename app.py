# Python In-built packages
from pathlib import Path
import PIL
import cv2
# External packages
import streamlit as st
import tempfile

# Local Modules
import settings
import helper

# Setting page layout
st.set_page_config(
    page_title="L&T PES Object Detection using YOLOv8",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("L&T PES Object Detection And Tracking using YOLOv8")

# Sidebar
st.sidebar.header("ML Model Config")

# Model Options
# model_type = st.sidebar.radio(
#     "Select Task", ['Detection', 'Segmentation'])

confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

# Selecting Detection Or Segmentation
# if model_type == 'Detection':
#     model_path = Path(settings.DETECTION_MODEL)
# elif model_type == 'Segmentation':
#     model_path = Path(settings.SEGMENTATION_MODEL)
model_path = settings.DETECTION_MODEL
# Load Pre-trained ML Model
try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

st.sidebar.header("Image/Video Config")
source_radio = st.sidebar.radio(
    "Select Source", settings.SOURCES_LIST)

source_img = None
# If image is selected
if source_radio == settings.IMAGE:
    source_img = st.sidebar.file_uploader(
        "Choose an image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))

    col1, col2 = st.columns(2)

    with col1:
        try:
            if source_img is None:
                default_image_path = str(settings.DEFAULT_IMAGE)
                default_image = PIL.Image.open(default_image_path)
                st.image(default_image_path, caption="Default Image",
                         use_column_width=True)
            else:
                uploaded_image = PIL.Image.open(source_img)
                st.image(source_img, caption="Uploaded Image",
                         use_column_width=True)
        except Exception as ex:
            st.error("Error occurred while opening the image.")
            st.error(ex)

    with col2:
        if source_img is None:
            default_detected_image_path = str(settings.DEFAULT_DETECT_IMAGE)
            default_detected_image = PIL.Image.open(
                default_detected_image_path)
            st.image(default_detected_image_path, caption='Detected Image',
                     use_column_width=True)
        else:
            if st.sidebar.button('Detect Objects'):
                res = model.predict(uploaded_image,
                                    conf=confidence
                                    )
                boxes = res[0].boxes
                res_plotted = res[0].plot()[:, :, ::-1]
                st.image(res_plotted, caption='Detected Image',
                         use_column_width=True)
                try:
                    with st.expander("Detection Results"):
                        for box in boxes:
                            st.write(box.data)
                except Exception as ex:
                    # st.write(ex)
                    st.write("No image is uploaded yet!")

elif source_radio == settings.VIDEO:
    source_video = st.sidebar.file_uploader(
        "Choose a video...", type=("mp4", "avi", "mov", "wmv"))

    col1, col2 = st.columns(2)
    print(col1, col2)
    with col1:
        try:
            if source_video is None:
                default_video_path = str(settings.DEFAULT_VIDEO)
                st.video(default_video_path, format="video/mp4")
            else:
                st.video(source_video, format="video/mp4")
        except Exception as ex:
            st.error("Error occurred while opening the video.")
            st.error(ex)

    with col2:
        if source_video is None:
            default_detected_video_path = str(settings.DEFAULT_DETECT_VIDEO)
            st.video(default_detected_video_path, format="video/mp4")
        else:
            is_display_tracker, tracker = helper.display_tracker_options();
            if st.sidebar.button('Detect Objects'):
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(source_video.read());
                try:
                    vid_cap = cv2.VideoCapture(
                        str(temp_file.name))
                    
                    st_frame = st.empty()
                    while True:
                        success, frame = vid_cap.read()
                        if success:
                            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                            # frame = cv2.resize(frame, (720, int(720*(9/16))))  # Resize if needed
                            helper._display_detected_frames(confidence,
                                                    model,
                                                    st_frame,
                                                    frame,
                                                    is_display_tracker,
                                                    tracker
                                                    )
                        else:
                            vid_cap.release()
                            break
                except Exception as e:
                    print("err", e)
                    st.sidebar.error("Error loading video: " + str(e))
    # helper.play_stored_video(confidence, model)

elif source_radio == settings.WEBCAM:
    helper.play_webcam(confidence, model)

elif source_radio == settings.RTSP:
    helper.play_rtsp_stream(confidence, model)

elif source_radio == settings.YOUTUBE:
    helper.play_youtube_video(confidence, model)
