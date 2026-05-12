@echo off
title Compressor de PDFs Profissional
echo ======================================================
echo        INICIANDO COMPRESSAO DE PDFS (EDP FIX)
echo ======================================================
echo.

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! Por favor, instale o Python.
    pause
    exit
)

:: Verifica se as bibliotecas estao instaladas
echo [1/2] Verificando bibliotecas...
python -c "import fitz, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Instalando bibliotecas necessarias...
    pip install pymupdf Pillow
)

:: Executa o script
echo [2/2] Processando PDFs na pasta...
python comprimir_pdfs.py

echo.
echo ======================================================
echo        PROCESSO CONCLUIDO COM SUCESSO!
echo ======================================================
echo.
pause
