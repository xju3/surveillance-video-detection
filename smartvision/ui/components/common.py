import streamlit as st
from common.settings import SESSION_KEYS, PROMPT_TEXT, LOCAL_DIRS, STAGE, KEY_NAMES
from common.utils import get_resource_dir
from common.loader import show_md_content
from ai.common.cv import cv_video_info
import os


def append_asistant_message(message):
    st.session_state[SESSION_KEYS.MESSAGES].append(
        {"role": "assistant", "content": message}
    )

def append_user_message(message):
    st.session_state[SESSION_KEYS.MESSAGES].append({"role": "user", "content": message})


def show_assistant_animation_message(message):
    with st.chat_message("assistant"):
        show_md_content(
            st,
            KEY_NAMES.FILE_LOADING_ANIMATION,
            message,
        )

def show_assistant_messages(chat_container):
    with chat_container:
        for message in st.session_state[SESSION_KEYS.MESSAGES]:
            if message["role"] != "system":  # 不显示系统消息
                with st.chat_message(message["role"]):
                    st.markdown(
                        message["content"],
                        unsafe_allow_html=True,
                    )

def on_file_uploaded(uploaded_files, next_stage):
    """处理视频上传"""
    if uploaded_files:
        video_dir, image_dir = get_resource_dir(st)
        os.makedirs(video_dir, exist_ok=True)  # 确保目录存在
        index = 1
        for uploaded_file in uploaded_files:
            file_path = os.path.join(video_dir, f"{index}-{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"文件 '{uploaded_file.name}' 已保存至 {video_dir}")
            index += 1
        # 存储文件
        st.session_state[SESSION_KEYS.UPLOADED_FILES] = uploaded_files
        
        # 获取视频时长信息，用于计费.
        videos = cv_video_info(video_dir)
        st.session_state[SESSION_KEYS.VIDEOS] = videos
        total = 0
        for video in videos:
            total += video["duration"]
        append_asistant_message(f"视频上传成功,共{len(uploaded_files)}个,总时长{total / 60}分钟")
        st.session_state[SESSION_KEYS.STAGE] = next_stage
        st.rerun()