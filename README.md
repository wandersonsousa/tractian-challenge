# 🏗️ baldor.com Scraper

Script para extração de dados de produtos utilizando Python e Docker.

## 🚀 Como executar com Docker

### 🔧 Build da imagem:

```
docker build -t product-scraper .
```

### 📦 Executar o scraper:

```
docker run -v $(pwd)/output:/app/output -e MAX_WORKERS=10 product-scraper --limit 10
```

### ✅ Isso irá:
- Executar o scraper
- Limitar para extrair **10 produtos**
- Utilizar até **10 workers** para paralelizar o processo
- Salvar os dados na pasta local `./output`

## 📁 Estrutura dos arquivos gerados

Os dados extraídos serão salvos na pasta `output`, contendo:
- ✅ Um arquivo JSON por produto com todas as informações estruturadas
- 📂 Subpastas com imagens, manuais, arquivos CAD e outros ativos relacionados (se existirem)

## ⚙️ Parâmetros disponíveis

- `--limit`: Limita a quantidade de produtos a serem extraídos.  
Exemplo: `--limit 10`

- `MAX_WORKERS` (variável de ambiente): Define o número de workers para execução em paralelo.  
Exemplo: `-e MAX_WORKERS=10`



## Streamlit

Você também pode executar o streamlit para buscar produtos por interface gráfica, basta instalar as dependências:

```bash
uv pip install -r requirements.txt
```

E rodar o cli do streamlit
```bash
streamlit run src/app.py
```
