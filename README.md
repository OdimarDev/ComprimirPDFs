# Compressor de PDF Pro

Um aplicativo simples e eficiente para comprimir arquivos PDF, mantendo a qualidade do texto e reduzindo drasticamente o tamanho das imagens.

## Funcionalidades

*   **Compressão de Imagens**: Reduz o tamanho das imagens internas do PDF.
*   **Preservação de Texto**: O texto permanece selecionável e pesquisável.
*   **Suporte a Subpastas**: Opção para processar arquivos recursivamente.
*   **Suporte a Senhas**: Campo para inserir senha de PDFs protegidos.
*   **Interface Gráfica**: Fácil de usar, sem necessidade de linha de comando.

## Requisitos para Desenvolvedores

Se você deseja rodar o script diretamente ou gerar o executável, instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Gerar o Executável (.exe)

1.  Instale o PyInstaller: `pip install pyinstaller`
2.  Execute o comando: `pyinstaller compressor_pdf_gui.spec`
3.  O arquivo final estará na pasta `dist/`.

## Autor
Desenvolvido com auxílio de Manus AI.
