# %%
import pandas as pd
import ast

# %%
# Configurações do Pandas para visualização completa

# Isso garante que você veja todas as colunas e o conteúdo completo das células longas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1000) # Tenta ajustar a largura da exibição no console

# %%
# Carregamento do dataset

path = "../data/raw/movies_metadata.csv"

# 'low_memory=False' é útil para arquivos CSV grandes ou complexos,
# ajuda o pandas a determinar melhor os tipos de dados.
df_metadata = pd.read_csv(path, low_memory=False)
print(f"Dataset '{path}' carregado com sucesso! \nTotal de linhas: {df_metadata.shape[0]} \nTotal de colunas: {df_metadata.shape[1]}")

# %% [markdown]
# ### Inspeção Inicial

# %%
print("--- Primeiras 5 linhas do DataFrame ---")
df_metadata.head()

# %%
print("\n--- Informações do DataFrame ---")
df_metadata.info()

# %%
print("\n--- Estatísticas Descritivas do DataFrame ---")
df_metadata.describe()

# %% 
print("\n--- Contagem de Valores Nulos por Coluna ---")
df_metadata.isnull().sum()

# %% [markdown]
# ### Colunas com Dicionários/JSONs Aninhados
# 'genres', 'production_companies', 'production_countries', 'spoken_languages', 'belongs_to_collection'.

# %% [markdown]
# ### Limpeza e Conversão de colunas com dicionários/JSON aninhados

# %% 
# Funções

# Conversão de strings que representam listas de dicionários para objetos Python
def safe_literal_eval(val):
    try:
        if isinstance(val,str) and val.strip():
            return ast.literal_eval(val)
        else:
            return []
    except (ValueError, SyntaxError):
        return []
    
# Extração de nomes de uma lista de dicionários
def extract_names(list_dicts):
    if isinstance(list_dicts, list):
        return [d['name'] for d in list_dicts if 'name' in d]
    return []

# %%
# Colunas que precisam ser convertidas de string para lista de dicionários
json_columns = ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'belongs_to_collection']

for col in json_columns:
    df_metadata[col] = df_metadata[col].apply(safe_literal_eval)

print("--- Colunas com dicionários aninhados convertidas para objetos Python ---")
print(df_metadata[json_columns].head()) 
print(df_metadata[json_columns].dtypes)

# %%
# Aplicar a função para extrair os nomes dos gêneros
df_metadata['genre_names'] = df_metadata['genres'].apply(extract_names)

print("\n--- Nomes de gêneros extraídos ---")
print(df_metadata[['genres', 'genre_names']].head())

# Aplicar a função para extrair os nomes das companhias de produção
df_metadata['production_company_names'] = df_metadata['production_companies'].apply(extract_names)

print("\n--- Nomes de companhias de produção extraídos ---")
print(df_metadata[['production_companies', 'production_company_names']].head())

# %%
# Novo Dataframe limpo
columns_to_drop = ['genres', 'overview', 'production_companies', 'production_countries', 'spoken_languages', 'belongs_to_collection', 'tagline']

df_metadata_clean = df_metadata.drop(columns=columns_to_drop)

# %%
df_metadata_clean.head()

# %% [markdown]
# ### Tratamento da Coluna `release_date`e Criação da coluna 'release_year'

# %%
print("\n--- Inspecionando 'release_date' antes da conversão ---")
print(df_metadata_clean['release_date'].head())
print(df_metadata_clean['release_date'].dtype)
print("Valores nulos em 'release_date' antes:", df_metadata_clean['release_date'].isnull().sum())

# %%
df_metadata_clean['release_date'] = pd.to_datetime(df_metadata_clean['release_date'], errors='coerce')

# %%
print("\n--- Inspecionando 'release_date' depois da conversão ---")
print(df_metadata_clean['release_date'].head())
print(df_metadata_clean['release_date'].dtype)
print("Valores nulos em 'release_date' depois:", df_metadata_clean['release_date'].isnull().sum())

# %%
df_metadata_clean['release_year'] = df_metadata_clean['release_date'].dt.year

# %%
df_metadata_clean[['release_date', 'release_year']]

# %% [markdown]
# ### Tratamento das Colunas Numéricas `budget` e `revenue`

# %%
print("\n--- Inspecionando 'budget' e 'revenue' antes da conversão ---")
print(df_metadata_clean[['budget', 'revenue']].head())
print(df_metadata_clean[['budget', 'revenue']].dtypes)

# %%
# Verificar valores não numéricos que podem estar atrapalhando
# Para 'budget'
non_numeric_budget = df_metadata_clean[pd.to_numeric(df_metadata_clean['budget'], errors='coerce').isna()]['budget'].unique()
print(f"\nValores não numéricos em 'budget' antes da conversão: {non_numeric_budget[:5]}...")

# Para 'revenue'
non_numeric_revenue = df_metadata_clean[pd.to_numeric(df_metadata_clean['revenue'], errors='coerce').isna()]['revenue'].unique()
print(f"Valores não numéricos em 'revenue' antes da conversão: {non_numeric_revenue[:5]}...")

# %%
# Converter para numérico tratando erros
df_metadata_clean['budget'] = pd.to_numeric(df_metadata_clean['budget'], errors='coerce')
df_metadata_clean['revenue'] = pd.to_numeric(df_metadata_clean['revenue'], errors='coerce')

print("\n--- Inspecionando 'budget' e 'revenue' depois da conversão ---")
print(df_metadata_clean[['budget', 'revenue']].head())
print(df_metadata_clean[['budget', 'revenue']].dtypes)

# %%
print("\nValores nulos em 'budget' depois da conversão:", df_metadata_clean['budget'].isnull().sum())
print("Valores nulos em 'revenue' depois da conversão:", df_metadata_clean['revenue'].isnull().sum())

# %% [markdown]
# ### Tratamento de Valores Ausentes (NaNs/NaTs) em Colunas Chave


# %%
critical_columns = ['title', 'vote_average', 'vote_count', 'budget', 'revenue', 'release_date', 'id']
print(df_metadata_clean[critical_columns].isnull().sum())

# %%
# 1. Tratar a coluna 'id': Garantir que seja numérica e sem nulos.

df_metadata_clean['id'] = pd.to_numeric(df_metadata_clean['id'], errors='coerce')
df_metadata_clean = df_metadata_clean.dropna(subset=['id'])
df_metadata_clean['id'] = df_metadata_clean['id'].astype(int)

# 2. Tratar a coluna 'title': Remover linhas sem título.

df_metadata_clean = df_metadata_clean.dropna(subset=['title'])

# %%
# 3. Tratar 'vote_average' e 'vote_count': Preencher nulos com 0.

df_metadata_clean[['vote_average', 'vote_count']].dtypes

df_metadata_clean['vote_average'] = df_metadata_clean['vote_average'].fillna(0)
df_metadata_clean['vote_count'] = df_metadata_clean['vote_count'].fillna(0)

# 4. Tratar 'budget' e 'revenue': Preencher nulos com 0.

df_metadata_clean['budget'] = df_metadata_clean['budget'].fillna(0)
df_metadata_clean['revenue'] = df_metadata_clean['revenue'].fillna(0)

# 5. Tratar 'release_date': Remover linhas sem data de lançamento.

df_metadata_clean = df_metadata_clean.dropna(subset=['release_date'])

print(f"\n--- DataFrame 'df_metadata_clean' após tratamento de Nulos/NaTs ---")
print(f"Dimensões finais: {df_metadata_clean.shape[0]} linhas, {df_metadata_clean.shape[1]} colunas")
print("\nContagem final de Nulos em Colunas Chave:")
print(df_metadata_clean[critical_columns].isnull().sum())

# %% [markdown]
# ### Carregamento, preparação e agregação do `df_ratings`

# %%
path_ratings = "../data/raw/ratings.csv"

df_ratings = pd.read_csv(path_ratings, low_memory=False)

print(f"\nDataset '{path_ratings}' carregado com sucesso! \nTotal de linhas: {df_ratings.shape[0]} \nTotal de colunas: {df_ratings.shape[1]}")

# %%
# Inspeção Inicial

print("\n--- Primeiras 5 linhas do DataFrame ---")
print(df_ratings.head())

print("\n--- Informações do DataFrame ---")
df_ratings.info()

print("\n--- Estatísticas Descritivas do DataFrame ---")
print(df_ratings.describe())

print("\n--- Contagem de Valores Nulos por Coluna ---")
print(df_ratings.isnull().sum())

# %% [markdown]
# ### Preparação e Agregação do `df_ratings`

# %%
df_ratings['movieId'] = pd.to_numeric(df_ratings['movieId'], errors='coerce')
df_ratings = df_ratings.dropna(subset=['movieId'])
df_ratings['movieId'] = df_ratings['movieId'].astype(int)

# %%
df_movie_ratings = df_ratings.groupby('movieId').agg(
    average_rating = ('rating', 'mean'),
    ratings_count = ('rating', 'count')
).reset_index()

df_movie_ratings

# %% [markdown]
# ### Mesclagem de `df_metadata_clean` com `df_movie_ratings`

# %%
df_final = pd.merge(df_metadata_clean, df_movie_ratings,
                    left_on='id',
                    right_on='movieId',
                    how='left')

# %%
df_final['average_rating'] = df_final['average_rating'].fillna(0)
df_final['ratings_count'] = df_final['ratings_count'].fillna(0)

df_final = df_final.drop(columns=['movieId'])

df_final.head()

# %% [markdown]
# ### Salvando o DataFrame Transformado

# %%
output_file_path = "../data/processed/movies_metadata_cleaned.csv"
df_final.to_csv(output_file_path, index=False)
print(f"\nDataFrame 'df_final' salvo com sucesso em: {output_file_path}")
