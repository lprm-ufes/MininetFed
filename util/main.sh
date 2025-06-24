#!/bin/bash

# Verifica se pelo menos um argumento foi passado
if [ $# -eq 0 ]; then
    echo "Uso: sh main.sh <arquivo1.py> <arquivo2.py> ..."
    exit 1
fi

# Itera sobre cada argumento (nome de arquivo Python)
for file in "$@"; do
    # Verifica se o arquivo existe
    if [ -f "$file" ]; then
        # Nome do arquivo base
        BASENAME=$(basename "$file")

        # Caminho de destino no diretório raiz do script
        DEST_FILE="temp_top.py"

        # Copia o arquivo para o diretório raiz do script
        echo "Copying $file to $DEST_FILE"
        cp "$file" "$DEST_FILE"

        # Executa o arquivo copiado
        echo "Running: sudo python3 $DEST_FILE"
        sudo python3 "$DEST_FILE"

        # Remove o arquivo copiado após a execução
        if [ "$DEST_FILE" != "$file" ]; then
            echo "Removing $DEST_FILE"
            rm "$DEST_FILE"
        fi
    else
        echo "Error: File $file not found."
    fi
done
