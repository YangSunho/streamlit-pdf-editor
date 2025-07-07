import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="PDF 페이지 추출기", layout="wide")
st.title("📄 PDF 페이지 선택 및 추출기")

# 세션 상태 초기화
if "selected_pages" not in st.session_state:
    st.session_state.selected_pages = set()
if "output_stream" not in st.session_state:
    st.session_state.output_stream = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

# 업로드 및 다운로드 영역 (상단 고정)
with st.container():
    top_col1, top_col2 = st.columns([3, 2])
    with top_col1:
        uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
        if uploaded_file:
            st.session_state.pdf_bytes = uploaded_file.read()

    with top_col2:
        if st.session_state.pdf_bytes and st.session_state.selected_pages:
            if st.button("📥 PDF 다운로드"):
                reader = PdfReader(io.BytesIO(st.session_state.pdf_bytes))
                writer = PdfWriter()
                for idx in sorted(st.session_state.selected_pages):
                    writer.add_page(reader.pages[idx])

                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)
                st.session_state.output_stream = output_stream

        if st.session_state.output_stream:
            st.download_button(
                label="📄 다운로드 시작",
                data=st.session_state.output_stream,
                file_name="추출된_페이지.pdf",
                mime="application/pdf"
            )

if st.session_state.pdf_bytes:
    doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")

    st.markdown("---")
    st.subheader("📌 추출할 페이지 선택")

    cols = st.columns(3)
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        col = cols[i % 3]
        with col:
            key = f"page_{i}"
            checked = st.checkbox(f"선택 {i + 1}페이지", key=key)
            if checked:
                st.session_state.selected_pages.add(i)
            else:
                st.session_state.selected_pages.discard(i)
            st.image(img, caption=f"페이지 {i + 1}", use_column_width=True)

    if st.session_state.selected_pages:
        st.success(f"✅ {len(st.session_state.selected_pages)}개 페이지 선택됨")
else:
    st.info("좌측에서 PDF 파일을 업로드해주세요.")
