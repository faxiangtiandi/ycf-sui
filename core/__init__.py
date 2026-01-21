# core/utils.py
import base64

def image_to_base64_bytesio(uploaded_file):
    """
    将文件对象转换为 base64 字符串（不依赖 Streamlit）。
    """
    if not uploaded_file:
        return ""
    try:
        if hasattr(uploaded_file, "getvalue"):
            raw = uploaded_file.getvalue()
        else:
            raw = uploaded_file.read()
        return base64.b64encode(raw).decode("utf-8")
    except Exception:
        return ""
