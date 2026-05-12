import os
import io
import sys
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from pathlib import Path
import threading
import base64

# Ícone em Base64 para embutir no script (opcional, mas bom para portabilidade)
# Para simplificar, vamos carregar do arquivo se existir, senão usar o padrão
ICON_PATH = "app_icon.ico"

def fmt(b):
    for u in ("B", "KB", "MB"):
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} MB"

class PDFCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compressor de PDF Pro")
        self.root.geometry("600x550")
        self.root.resizable(False, False)

        # Tentar carregar o ícone da janela
        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except:
                pass

        # Variáveis
        self.folder_path = tk.StringVar()
        self.recursive = tk.BooleanVar(value=False)
        self.quality = tk.IntVar(value=30)
        self.dpi = tk.IntVar(value=150)
        self.pdf_password = tk.StringVar()
        self.is_processing = False

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Seleção de Pasta
        ttk.Label(main_frame, text="Pasta de Origem:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.folder_path, width=50).grid(row=1, column=0, padx=(0, 10))
        ttk.Button(main_frame, text="Procurar", command=self.browse_folder).grid(row=1, column=1)

        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=15)

        ttk.Checkbutton(options_frame, text="Incluir subpastas (Recursivo)", variable=self.recursive).grid(row=0, column=0, sticky=tk.W)
        
        # Campo de Senha
        ttk.Label(options_frame, text="Senha do PDF (se houver):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Entry(options_frame, textvariable=self.pdf_password, show="*", width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        ttk.Label(options_frame, text="Qualidade (1-100):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Scale(options_frame, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=(10, 0))
        ttk.Label(options_frame, textvariable=self.quality).grid(row=2, column=2, pady=(10, 0))

        ttk.Label(options_frame, text="DPI (Resolução):").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        dpi_combo = ttk.Combobox(options_frame, textvariable=self.dpi, values=[72, 96, 150, 200, 300], width=5)
        dpi_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        # Progresso e Status
        self.status_label = ttk.Label(main_frame, text="Pronto para iniciar", foreground="gray")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=540, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=2, pady=10)

        self.log_text = tk.Text(main_frame, height=10, width=70, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.grid(row=5, column=0, columnspan=2)

        # Botão Iniciar
        self.start_button = ttk.Button(main_frame, text="INICIAR COMPRESSÃO", command=self.start_process_thread)
        self.start_button.grid(row=6, column=0, columnspan=2, pady=15)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def comprimir_arquivo(self, input_path, output_path, quality, dpi, password):
        try:
            tam_antes = os.path.getsize(input_path)
            doc_orig = fitz.open(input_path)
            
            # Tentar desbloquear se estiver protegido
            if doc_orig.is_encrypted:
                if not doc_orig.authenticate(password):
                    doc_orig.close()
                    return False, 0, 0, "Senha incorreta ou necessária"
            
            doc_novo = fitz.open()
            
            for page_orig in doc_orig:
                pix = page_orig.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality, optimize=True)
                
                rect = page_orig.rect
                page_nova = doc_novo.new_page(width=rect.width, height=rect.height)
                page_nova.insert_image(rect, stream=buf.getvalue())
                
                text_dict = page_orig.get_text("dict")
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                try:
                                    page_nova.insert_text(
                                        span["origin"], 
                                        span["text"], 
                                        fontsize=span["size"],
                                        fontname="helv",
                                        color=(0, 0, 0),
                                        fill_opacity=0
                                    )
                                except:
                                    continue

            doc_novo.save(output_path, garbage=4, deflate=True)
            doc_orig.close()
            doc_novo.close()
            
            tam_depois = os.path.getsize(output_path)
            reducao = (1 - tam_depois/tam_antes) * 100
            return True, tam_antes, tam_depois, reducao
        except Exception as e:
            return False, 0, 0, str(e)

    def start_process_thread(self):
        if not self.folder_path.get():
            messagebox.showwarning("Aviso", "Selecione uma pasta primeiro!")
            return
        
        if self.is_processing:
            return

        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        caminho_base = Path(self.folder_path.get())
        qualidade = self.quality.get()
        dpi = self.dpi.get()
        recursivo = self.recursive.get()
        senha = self.pdf_password.get()

        if recursivo:
            arquivos = list(caminho_base.rglob("*.pdf"))
        else:
            arquivos = list(caminho_base.glob("*.pdf"))

        arquivos = [f for f in arquivos if "comprimidos" not in str(f)]

        if not arquivos:
            self.log("Nenhum arquivo PDF encontrado.")
            self.is_processing = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            return

        self.progress["maximum"] = len(arquivos)
        self.progress["value"] = 0
        sucesso_total = 0

        for i, f in enumerate(arquivos):
            self.status_label.config(text=f"Processando {i+1}/{len(arquivos)}: {f.name}")
            
            if recursivo:
                rel_path = f.relative_to(caminho_base)
                pasta_saida = caminho_base / "comprimidos" / rel_path.parent
            else:
                pasta_saida = caminho_base / "comprimidos"
            
            pasta_saida.mkdir(parents=True, exist_ok=True)
            output_file = pasta_saida / f.name

            ok, t_antes, t_depois, info = self.comprimir_arquivo(str(f), str(output_file), qualidade, dpi, senha)
            
            if ok:
                self.log(f"✅ {f.name}: {fmt(t_antes)} -> {fmt(t_depois)} (-{info:.1f}%)")
                sucesso_total += 1
            else:
                self.log(f"❌ Erro em {f.name}: {info}")
            
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.status_label.config(text="Processo finalizado!")
        self.log(f"\n✨ Finalizado! {sucesso_total}/{len(arquivos)} arquivos processados.")
        messagebox.showinfo("Sucesso", f"Processo concluído!\n{sucesso_total} arquivos comprimidos na pasta 'comprimidos'.")
        
        self.is_processing = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCompressorApp(root)
    root.mainloop()
