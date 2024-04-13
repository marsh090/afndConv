# Conversor de Autômatos Finitos

Este é um projeto de conversão de autômatos finitos não determinísticos (AFND) para autômatos finitos determinísticos (AFD), implementado em Python.

## Funcionalidades

- **Parse de Arquivos**: Suporta a leitura de autômatos representados em arquivos XML (formato JFlap) e texto simples.
- **Conversão AFND para AFD**: Transforma um AFND em um AFD equivalente.
- **Exportação de Resultados**: Salva o AFD resultante em um arquivo de texto.

## Como Usar

1. **Instalação**: Clone este repositório em sua máquina local.

2. **Execução**: Execute o script `main.py`, fornecendo o caminho para o arquivo de entrada. Por exemplo:

    ```bash
    python main.py entrada.jflap
    ```

3. **Saída**: Após a execução, o script criará um arquivo `saida.txt` contendo o AFD resultante.

## Requisitos

- Python 3.x
- Biblioteca ElementTree (para processamento XML)


```bash
python main.py entrada.jflap
```

Isso produzirá um arquivo saida.txt com o AFD resultante.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Autor
Desenvolvido por Lucas Zanon Guarnier.
