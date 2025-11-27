# Pipeline de Dados (Spark) - Sistema de Recomendação Agrícola Inteligente

Guia didatico (projeto universitario) para executar o pipeline Spark com Parquet em todas as camadas. Mantemos tudo simples, com carinho: passo a passo local, alternativa via Docker e notas de personalizacao.

## Visao geral

- **Bronze (`data/bronze/dados_brutos.parquet`)**: une producao, chuva e temperatura; renomeia colunas climaticas ambiguas; adiciona `data_ingestao`.
- **Silver (`data/silver/dados_limpos.parquet`)**: normaliza nomes, imputa numericos (mediana), preenche textos ("Unknown"), remove outliers (IQR em `PRODUCTION`, `AREA`, `YIELD`), padroniza texto e filtra culturas (MAIZE, RICE, WHEAT, BARLEY); gera `snake_case` e `data_processamento`.
- **Gold (`data/gold/*.parquet`)**: agregacoes de producao anual, desempenho regional, sazonalidade/clima, tendencia de rendimento, benchmark vs media nacional, perfil climatico e volatilidade (um Parquet por tabela).
- **Bancos (opcional)**: notebooks para carregar Silver/Gold em SQLite e Postgres.

## Estrutura principal

- `spark_jobs/config.py`: caminhos das camadas (use `PIPELINE_HOME` para alterar raiz).
- `spark_jobs/spark_session_manager.py`: criacao da SparkSession.
- `arquivo_base_silver.py`: funcoes de limpeza, outliers e pipeline Silver.
- `notebooks/*_spark.ipynb`: pipeline completo (inclui `00_setup_spark_parquet.ipynb` para preparar ambiente).
- `data/bronze|silver|gold`: saidas Parquet.

## Pre-requisitos (execucao local)

- Python 3.11+.  
- Java/OpenJDK 8+ no PATH (necessario para PySpark) — teste com `java -version`.  
- Kaggle (se for baixar datasets): `~/.kaggle/kaggle.json` ou variaveis `KAGGLE_USERNAME`/`KAGGLE_KEY`.  
- Postgres opcional: `.env` com `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `PG_DATABASE`.

## Passo a passo local

1) Criar e ativar ambiente virtual  
   - Windows (PowerShell):  
     ```
     python -m venv .venv
     .\.venv\Scripts\Activate
     ```
   - Linux/macOS:  
     ```
     python -m venv .venv
     source .venv/bin/activate
     ```

2) Instalar dependencias  
   ```
   pip install -r requirements.txt
   ```

3) Configurar Kaggle (se precisar baixar dados)  
   - Pegue `kaggle.json` (Kaggle > My Account > Create New Token) e coloque em `~/.kaggle/kaggle.json`; ou abra `notebooks/00_setup_spark_parquet.ipynb` e preencha `KAGGLE_USERNAME`/`KAGGLE_KEY` para gerar o json automaticamente.

4) (Opcional) Configurar Postgres  
   - Crie `.env` na raiz com `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `PG_DATABASE`.

5) Validar ambiente  
   - Rode `notebooks/00_setup_spark_parquet.ipynb`: checa Java, instala deps, cria pastas, permite criar `kaggle.json` e faz smoke test Parquet. É o melhor “assistente” para iniciantes: preencha `KAGGLE_USERNAME`/`KAGGLE_KEY` se precisar baixar dados.

6) Executar pipeline (ordem sugerida)  
   1. `notebooks/01_bronze_layer_spark.ipynb`  
   2. `notebooks/02_silver_layer_spark.ipynb`  
   3. `notebooks/03_gold_layer_spark.ipynb`  
   4. `notebooks/04_load_to_sqlite_spark.ipynb`  
   5. `notebooks/05_create_database_pg_schema_spark.ipynb`  
   6. `notebooks/06_load_to_postgres_spark.ipynb`  
   7. Opcional: `notebooks/analysis/data_quality_report_spark.ipynb` e `notebooks/analysis/SQL_queries_spark.ipynb`.

## Rodar via Docker (sem instalar Java local)

Use a imagem `jupyter/pyspark-notebook`:

- Windows (PowerShell):

  ```
  docker run --rm -it -p 8888:8888 -v ${PWD}:/home/jovyan/work jupyter/pyspark-notebook:latest
  ```
- Linux/macOS:

  ```
  docker run --rm -it -p 8888:8888 -v $(pwd):/home/jovyan/work jupyter/pyspark-notebook:latest
  ```
- Com Kaggle montado (PowerShell):

```
  docker run --rm -it -p 8888:8888 
    -v ${PWD}:/home/jovyan/work 
    -v ${HOME}\\.kaggle:/home/jovyan/.kaggle 
    jupyter/pyspark-notebook:latest
```

- Com Kaggle montado (Linux/macOS):

```
docker run --rm -it -p 8888:8888 \
  -v $(pwd):/home/jovyan/work \
  -v ${HOME}/.kaggle:/home/jovyan/.kaggle \
  jupyter/pyspark-notebook:latest
```

Depois de rodar o comando, o terminal mostra uma URL com token (ex.: `http://127.0.0.1:8888/?token=...`). Copie essa URL e cole no navegador. Os notebooks estao na pasta `work/` (que e o seu repo). Se precisar instalar dependencias extras dentro do container:

```
docker ps          # pega o CONTAINER ID
docker exec -it CONTAINER_ID bash
pip install -r /home/jovyan/work/requirements.txt
```

Em seguida, rode os notebooks na ordem dentro do Jupyter:
- `00_setup_spark_parquet.ipynb` (valida ambiente, permite criar kaggle.json preenchendo username/key; recomendado começar por ele)
- `01_bronze_layer_spark.ipynb`
- `02_silver_layer_spark.ipynb`
- `03_gold_layer_spark.ipynb`
- `04_load_to_sqlite_spark.ipynb`
- `05_create_database_pg_schema_spark.ipynb`
- `06_load_to_postgres_spark.ipynb`
- (opcionais) `notebooks/analysis/*_spark.ipynb`

## Teste rapido (linha unica)

```
python - <<'PY'
from pyspark.sql import SparkSession, Row, functions as F
from pathlib import Path
spark = SparkSession.builder.getOrCreate()
tmp = Path('data/_tmp_spark_check.parquet')
df = spark.createDataFrame([Row(id=i) for i in range(3)]).withColumn('ts', F.current_timestamp())
df.write.mode('overwrite').parquet(str(tmp))
print('written:', tmp)
spark.read.parquet(str(tmp)).show()
import shutil; shutil.rmtree(tmp, ignore_errors=True)
spark.stop()
PY
```

## Personalizacao

- Caminhos: ajuste `PIPELINE_HOME` ou edite `spark_jobs/config.py`.
- Outliers: altere a lista em `arquivo_base_silver.py` (padrao: `PRODUCTION`, `AREA`, `YIELD`).
- Paralelismo Spark: ajuste em `spark_jobs/spark_session_manager.py` (ex.: `spark.sql.shuffle.partitions`).

## Dicas

- Ative a venv antes de abrir notebooks locais.
- Se ja tiver `data/bronze/dados_brutos.parquet`, pode iniciar no Silver.
- Em nuvem (Databricks/EMR), reutilize notebooks e modulos alterando apenas caminhos em `config.py`.
- Para reprocessar, rode Bronze -> Silver -> Gold; as escritas sao overwrite por padrao.

## Artefatos principais

- Parquet: `data/bronze/dados_brutos.parquet`, `data/silver/dados_limpos.parquet`, `data/gold/*.parquet`
- Codigo: `arquivo_base_silver.py`, `spark_jobs/config.py`, `spark_jobs/spark_session_manager.py`
- Notebooks: `notebooks/*_spark.ipynb`, `notebooks/analysis/*_spark.ipynb`


## Problemas para conseguir a kaggle key?

- Faça login no kaggle
- Acesse o link: `https://www.kaggle.com/settings`
- Procure por: **Legacy API Credentials**
