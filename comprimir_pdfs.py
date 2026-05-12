#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║         COMPRESSOR DE PDF — Versão Reconstrutor de Texto        ║
║         Fidelidade Total, Texto Real e Tamanho Mínimo            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import argparse
import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path

def fmt(b):
    for u in ("B", "KB", "MB"):
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} MB"

def comprimir_arquivo(input_path, output_path, quality=30, dpi=150):
    try:
        print(f"\n📄 Processando: {Path(input_path).name}")
        tam_antes = os.path.getsize(input_path)
        
        doc_orig = fitz.open(input_path)
        doc_novo = fitz.open()
        
        for page_orig in doc_orig:
            # 1. Renderiza a página como imagem comprimida
            pix = page_orig.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            
            # 2. Cria página nova e insere a imagem
            rect = page_orig.rect
            page_nova = doc_novo.new_page(width=rect.width, height=rect.height)
            page_nova.insert_image(rect, stream=buf.getvalue())
            
            # 3. Extrai e reinsere o texto (invisível para manter a fidelidade da imagem)
            # O texto fica "atrás" ou "transparente" apenas para busca e cópia
            text_dict = page_orig.get_text("dict")
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Insere o texto na mesma posição, mas com cor transparente ou oculta
                            # Para garantir que o usuário veja a imagem mas selecione o texto
                            try:
                                page_nova.insert_text(
                                    span["origin"], 
                                    span["text"], 
                                    fontsize=span["size"],
                                    fontname="helv", # Fonte padrão para evitar erros
                                    color=(0, 0, 0),
                                    fill_opacity=0 # Texto invisível
                                )
                            except:
                                continue

        # Salva o novo documento
        doc_novo.save(output_path, garbage=4, deflate=True)
        doc_orig.close()
        doc_novo.close()
        
        tam_depois = os.path.getsize(output_path)
        reducao = (1 - tam_depois/tam_antes) * 100
        print(f"✅ Concluído | {fmt(tam_antes)} -> {fmt(tam_depois)} (-{reducao:.1f}%)")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Compressor de PDF (Reconstrutor)")
    parser.add_argument("entrada", nargs="?", default=".", help="Pasta ou arquivo PDF")
    parser.add_argument("-q", "--qualidade", type=int, default=30, help="Qualidade (1-100)")
    parser.add_argument("-d", "--dpi", type=int, default=150, help="DPI de renderização")
    
    args = parser.parse_args()
    caminho = Path(args.entrada).resolve()
    
    if caminho.is_file():
        arquivos = [caminho]
        pasta_saida = caminho.parent / "comprimidos"
    else:
        arquivos = sorted(list(caminho.glob("*.pdf")))
        arquivos = [f for f in sorted(arquivos, key=os.path.getmtime, reverse=True) if "comprimidos" not in str(f)]
        pasta_saida = caminho / "comprimidos"

    pasta_saida.mkdir(exist_ok=True)
    print(f"🚀 Iniciando compressão de {len(arquivos)} arquivo(s)...")

    sucesso = 0
    for f in arquivos:
        if comprimir_arquivo(str(f), str(pasta_saida / f.name), args.qualidade, args.dpi):
            sucesso += 1

    print(f"\n✨ Finalizado! {sucesso}/{len(arquivos)} arquivos na pasta 'comprimidos'.")

if __name__ == "__main__":
    main()


