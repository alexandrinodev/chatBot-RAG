"""Chain de consulta com validação antes da busca e depois da geração."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from guardrails import SYSTEM_PROMPT, montar_dados, validar_pergunta, validar_resposta


def criar_chain_segura(banco_vetores, llm, segredos=()):
    retriever = banco_vetores.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{dados}"),
    ])
    gerador = prompt | llm | StrOutputParser()

    def responder(pergunta):
        pergunta = validar_pergunta(pergunta)
        documentos = retriever.invoke(pergunta)
        dados = montar_dados(pergunta, documentos)
        resposta = gerador.invoke({"dados": dados})
        return validar_resposta(resposta, segredos)

    return RunnableLambda(responder)
