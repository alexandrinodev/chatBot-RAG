# Assistente RAG de Políticas Internas

Chat em português para consultar um PDF de políticas de RH, usando Streamlit,
LangChain, Google Gemini e FAISS.

O aplicativo divide o documento em blocos, gera embeddings e busca os trechos
relacionados à pergunta. O Gemini recebe esses trechos para elaborar a resposta.
O histórico aparece na interface, mas perguntas anteriores não são enviadas ao modelo.

## Requisitos

- Python 3.12 (versão usada no desenvolvimento).
- Uma chave da API Gemini, criada no [Google AI Studio](https://aistudio.google.com/apikey).
- Um PDF com texto selecionável para consulta.

## Executar localmente

Na pasta do projeto, execute:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

No Windows (PowerShell), ative o ambiente com `.venv\Scripts\Activate.ps1`
e copie a configuração com `Copy-Item .env.example .env`.

Preencha `GOOGLE_API_KEY` no `.env`. Os modelos podem ser ajustados nas variáveis
`GEMINI_MODEL` (conversa) e `GEMINI_EMBEDDING_MODEL` (embeddings).
Coloque seu documento em `data/politica_rh.pdf` e inicie:

```bash
streamlit run app_basic.py
```

## Estrutura

```text
app_basic.py              # Aplicação principal com Gemini
data/                    # PDF local e instruções
docs/                    # Material local de estudo
examples/app_openai.py    # Exemplo original com OpenAI
examples/requirements.txt # Dependências adicionais do exemplo
.env.example             # Configuração sem credenciais
requirements.txt         # Dependências da aplicação principal
```

## Embeddings e limites

O banco vetorial fica em memória com `st.cache_resource`, evitando gerar novamente
os embeddings do PDF a cada pergunta. Reiniciar o servidor, alterar o conteúdo do
documento, a chave ou o modelo de embeddings exige uma nova indexação.
Cada pergunta ainda gera um embedding para buscar trechos e uma chamada ao modelo
de conversa. O cache não é persistido em disco.

Se ocorrer erro 429, aguarde a renovação da cota antes de tentar novamente.
Consulte os limites do seu projeto no [Google AI Studio](https://ai.dev/rate-limit).
Os trechos do PDF e as perguntas são enviados à API configurada.

## Exemplo com OpenAI

O exemplo em `examples/` mantém a implementação original e não utiliza o cache
da aplicação principal. Para executá-lo, preencha `OPENAI_API_KEY` no `.env`:

```bash
python -m pip install -r examples/requirements.txt
streamlit run examples/app_openai.py
```

## Enviar ao GitHub

Crie um repositório vazio no GitHub. Depois, na pasta deste projeto:

```bash
git init
git add .
git status --short
git commit -m "Organiza assistente RAG com Gemini"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

O `.gitignore` exclui `.env`, ambientes virtuais, PDFs, dados locais e índices
vetoriais. Apenas `.env.example` é incluído como modelo de configuração.
