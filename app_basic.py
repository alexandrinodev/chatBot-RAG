"""
Assistente RAG de Políticas Internas (RH)
- Streamlit (interface)
- LangChain com LCEL (orquestração)
- FAISS (banco vetorial)
- Google Gemini (embeddings + LLM)
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_google_genai._common import GoogleGenerativeAIError
from guardrails import GuardrailError, MAX_PERGUNTA, validar_pergunta
from rag import criar_chain_segura


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

st.title("Assistente RAG — Políticas Internas")

if not os.getenv("GOOGLE_API_KEY"):
    st.error("Configure GOOGLE_API_KEY no arquivo .env para usar o Gemini.")
    st.stop()


#logica do contexto do RAG
def carregar_pdf(): #ler o pdf e extrair o texto
    caminho_pdf = BASE_DIR / "data" / "politica_rh.pdf"
    if not caminho_pdf.is_file():
        st.info("Adicione seu PDF em data/politica_rh.pdf para começar.")
        st.stop()
    pdf_loader = PyPDFLoader(str(caminho_pdf))
    texto = pdf_loader.load()
    return texto

texto_pdf = carregar_pdf()

def separar_em_blocos(texto_pdf):
    separador = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
        )
    lista_blocos = separador.split_documents(texto_pdf)
    
    return lista_blocos


lista_blocos = separar_em_blocos(texto_pdf)
# print(len(lista_blocos))
# print(lista_blocos[1])
#logica do agente de IA

@st.cache_resource(show_spinner="Preparando a busca no PDF...")
def criar_banco_vetores(lista_blocos, modelo_embedding, api_key):
    ferramenta_embedding = GoogleGenerativeAIEmbeddings(
        model=modelo_embedding,
        google_api_key=api_key,
    )
    banco_vetores = FAISS.from_documents(lista_blocos, ferramenta_embedding)
    return banco_vetores

try:
    banco_vetores = criar_banco_vetores(
        lista_blocos,
        os.getenv("GEMINI_EMBEDDING_MODEL") or "gemini-embedding-001",
        os.environ["GOOGLE_API_KEY"],
    )
except GoogleGenerativeAIError as erro:
    if getattr(erro.__cause__, "code", None) != 429:
        raise
    st.warning(
        "O limite de embeddings do Gemini foi atingido. Aguarde pelo menos um minuto "
        "e recarregue a página. Se persistir, consulte a cota do projeto no Google AI Studio."
    )
    st.stop()

def criar_chain_agente(banco_vetores):
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL") or "gemini-3.8-flash",
        temperature=0,
        max_output_tokens=1500,
    )
    segredos = tuple(
        os.environ[nome] for nome in ("GOOGLE_API_KEY", "OPENAI_API_KEY")
        if os.getenv(nome)
    )
    return criar_chain_segura(banco_vetores, llm, segredos)


#interface

# ============================================================
# INTERFACE
# ============================================================

# carregar chain e vector store
chain = criar_chain_agente(banco_vetores)

# inicia a lista de mensagens
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# exibe as mensagens na tela
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

prompt = st.chat_input("Pergunte sobre as políticas da empresa...", max_chars=MAX_PERGUNTA)
if prompt :
    try:
        prompt = validar_pergunta(prompt)
    except GuardrailError as erro:
        st.warning(str(erro))
        st.stop()
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.text(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando..."):
            try:
                answer = chain.invoke(prompt)
            except GuardrailError as erro:
                st.warning(str(erro))
                st.stop()
            except GoogleGenerativeAIError as erro:
                if getattr(erro.__cause__, "code", None) != 429:
                    raise
                st.warning(
                    "O limite de embeddings do Gemini foi atingido. "
                    "Aguarde pelo menos um minuto e envie sua pergunta novamente."
                )
                st.stop()
            st.text(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
