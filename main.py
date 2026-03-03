import streamlit as st
from PIL import Image, ImageOps
import os
from pillow_heif import register_heif_opener
import io

# Inicializa suporte para HEIF (iPhone)
register_heif_opener()

def resize_res(im):
    """Redimensiona a imagem mantendo a proporção (Cover)."""
    return ImageOps.cover(im, (1200, 1600))

def process_image(im, target_format="JPEG"):
    """Converte para RGB (removendo transparência) e prepara para salvar."""
    if im.mode in ('RGBA', 'P'):
        background = Image.new('RGB', im.size, (255, 255, 255))
        mask = im.split()[3] if im.mode == 'RGBA' else None
        background.paste(im, mask=mask)
        return background
    return im.convert('RGB')

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Image Resizer & Converter", page_icon="📸")

st.title("📸 Image Resizer & Converter")
st.markdown("Converta suas imagens para **JPG** e redimensione para **1200x1600** automaticamente.")

# Upload de arquivos (Streamlit lida com arquivos em memória, o que é mais seguro)
uploaded_files = st.file_uploader(
    "Escolha as imagens", 
    type=['webp', 'heic', 'png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"{len(uploaded_files)} arquivos carregados.")
    
    col1, col2 = st.columns(2)
    
    # Botões de ação
    convert_btn = col1.button("Apenas Converter para JPG")
    resize_btn = col2.button("Redimensionar (1200x1600)")

    if convert_btn or resize_btn:
        progress_bar = st.progress(0)
        status_text = st.empty()
        processed_images = []

        for i, file in enumerate(uploaded_files):
            try:
                # Abrir imagem
                img = Image.open(file)
                
                # Processamento
                if resize_btn:
                    img = resize_res(img)
                
                img_final = process_image(img)

                # Salvar em um buffer de memória (BytesIO)
                buf = io.BytesIO()
                img_final.save(buf, format="JPEG")
                byte_im = buf.getvalue()
                
                processed_images.append({
                    "name": f"{os.path.splitext(file.name)[0]}_processed.jpg",
                    "content": byte_im
                })

                # Atualizar progresso
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processando: {file.name}")

            except Exception as e:
                st.error(f"Erro ao processar {file.name}: {e}")

        st.success("✅ Processamento concluído!")

        # Opção de Download
        if processed_images:
            st.markdown("### Baixe seus arquivos:")
            for img_data in processed_images:
                st.download_button(
                    label=f"Download {img_data['name']}",
                    data=img_data['content'],
                    file_name=img_data['name'],
                    mime="image/jpeg"
                )