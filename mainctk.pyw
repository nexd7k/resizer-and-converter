from PIL import Image, ImageOps
import os
import customtkinter as ctk
from tkinter.filedialog import askdirectory
import threading
from pillow_heif import register_heif_opener


register_heif_opener()

# Adicionando uma variável global para armazenar o caminho escolhido
path = ""

#Função para escolher a pasta das imagens
def escolher_caminho():
    global path  # Tornando a variável global para ser acessada fora da função
    path = rf"{askdirectory()}"
    return path

# Função para definir nova resolução da imagem
def resize_res(im):
    im2 = ImageOps.cover(im, (1200, 1600))
    return im2

# Função para converter as imagens em uma thread separada
def convert():
    if path:
        files = os.listdir(path)
        extensions = ['webp', 'heic', 'png']
        try:
            for file in files:
                ext = file.split('.')[-1].lower()
                if ext in extensions:
                    im = Image.open(os.path.join(path, file))

                    if im.mode in ('RGBA', 'P'):
                        conv_im = Image.new('RGB', im.size, (255, 255, 255))
                        conv_im.paste(im, mask=im.split()[3] if im.mode == 'RGBA' else None)
                    else:
                        conv_im = im.convert('RGB')
                    
                    new_file = file.rsplit('.', 1)[0] + '.jpg'
                    conv_im.save(os.path.join(path, new_file), format="JPEG")
                    print("As imagens foram convertidas com sucesso. ")
        except Exception as e:
            print(f'Não foi possível converter as imagens: {e}')

# Função para redimensionar as imagens em uma thread separada
def resize():
    if path:
        files = os.listdir(path)
        extensions = ['jpg', 'jpeg', 'png']
        new_path = rf'{path}\resized_images'
        try:
            for file in files:
                ext = file.split('.')[-1].lower()
                if ext in extensions:
                    im = Image.open(os.path.join(path, file))
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    im_resized = resize_res(im)

                    if im_resized.mode in ('RGBA', 'P'):
                        background = Image.new('RGB', im_resized.size, (255, 255, 255))
                        background.paste(im_resized, mask=im_resized.split()[3] if im_resized.mode == 'RGBA' else None)
                        im_resized = background
                    else:
                        im_resized = im_resized.convert('RGB')

                    filepath = os.path.join(new_path, f"{file}-resized.jpg")
                    im_resized.save(filepath)
            print('Todas as imagens foram redimensionadas com sucesso.')
        except Exception as e:
            print(f'Ocorreu um erro ao redimensionar as imagens: {e}')

# Criando uma interface para o resizer
#Janela no modo escuro
ctk.set_appearance_mode("dark")

# Configurando a interface do app
app = ctk.CTk()
app.geometry("200x210")
app.title('Image Resizer')

# Adicionando o Botão para escolher o caminho
button = ctk.CTkButton(app, text = "Escolha a pasta", command=escolher_caminho)
button.grid(row=3, column=3, padx=30, pady=20)

# Adicionando um botão para iniciar o processo de resize
process_button = ctk.CTkButton(app, text="Redimensionar Imagens", command=lambda: threading.Thread(target=resize).start())
process_button.grid(row=4, column=3, padx=30, pady=20)

# Adicionando um botão para iniciar o processo de conversão
process_button = ctk.CTkButton(app, text="Converter Imagens", command=lambda: threading.Thread(target=convert).start())
process_button.grid(row=5, column=3, padx=30, pady=20)

app.mainloop()
