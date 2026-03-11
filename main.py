import streamlit as st
from PIL import Image, ImageOps
import os
from pillow_heif import register_heif_opener
import io
import zipfile

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

# Chave dinâmica para resetar o file_uploader
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Escolha as imagens", 
    type=['webp', 'heic', 'png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.info(f"{len(uploaded_files)} arquivos carregados.")
    
    col1, col2, col3 = st.columns(3)
    
    # Botões de ação
    convert_btn = col1.button("Apenas Converter para JPG")
    resize_btn = col2.button("Redimensionar (1200x1600)")
    clear_btn = col3.button("Limpar Imagens Carregadas")

    # Limpar imagens carregadas
    if clear_btn:
        st.session_state.uploader_key += 1
        st.rerun()

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

        if processed_images:
            st.markdown("### Baixe seus arquivos:")
            
            # 1. Criar um buffer na memória para o arquivo ZIP
            zip_buffer = io.BytesIO()
            
            # 2. Criar o arquivo ZIP e adicionar as imagens
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for img_data in processed_images:
                    zip_file.writestr(img_data['name'], img_data['content'])
            
            # 3. Botão para baixar o arquivo completo
            st.download_button(
                label="Baixar Imagens Processadas",
                data=zip_buffer.getvalue(),
                file_name="imagens_processadas.zip",
                mime="application/zip"
            )
