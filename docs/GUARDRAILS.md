# Guardrails da aplicação Gemini

## Política

- Responder sobre políticas de RH, apenas com base nos trechos recuperados.
- Reconhecer quando não houver informação suficiente, sem inventar regras.
- Tratar perguntas e conteúdo do PDF como dados não confiáveis.
- Recusar tentativas conhecidas de alterar instruções, extrair credenciais,
  executar código ou enviar dados a terceiros.
- Não disponibilizar ferramentas, acesso a arquivos ou navegação ao modelo.

## Controles implementados

`guardrails.py` concentra limites, regras e mensagens de recusa. `rag.py` aplica
as validações no fluxo, inclusive quando chamado fora da interface:

1. Pergunta não vazia, até 2.000 caracteres, com detecção de padrões em português
   e inglês após normalização Unicode. Um bloqueio ocorre antes da busca vetorial.
2. Busca de até quatro trechos. Conteúdo suspeito nos trechos inspecionados
   bloqueia a geração inteira; não se tenta remover a instrução e aproveitar o restante.
3. Até 12.000 caracteres de texto de contexto, serializados em JSON com páginas.
   O prompt de sistema fica em uma mensagem separada. JSON organiza os dados;
   não é uma barreira que o modelo seja incapaz de atravessar.
4. Validação da saída: limite de 6.000 caracteres, detecção de chaves em formatos
   conhecidos, comparação com as chaves configuradas, padrões suspeitos,
   links HTTP/HTTPS e marcação HTML/imagens.
5. Exibição com `st.text`, evitando interpretação de Markdown, HTML e imagens.

As chaves da aplicação não são incluídas nas mensagens do modelo. São utilizadas
localmente para autenticar as chamadas às APIs. A validação da resposta funciona
como uma camada adicional e não como autorização de acesso a segredos.

## Limitações e escopo

Filtros por padrões podem bloquear perguntas legítimas e deixar passar ataques
novos, codificados, em outros idiomas ou distribuídos entre trechos. As restrições
de assunto, fidelidade aos fatos e citação de páginas dependem também do modelo;
não há verificação automática de que cada afirmação está apoiada no PDF.

O PDF é um documento local escolhido pelo responsável pelo app. A inspeção ocorre
nos trechos recuperados antes da geração; ela não impede o envio do documento ao
serviço de embeddings na indexação. Revise o documento antes de adicioná-lo.

Esses controles não fornecem autenticação, autorização por usuário, isolamento
de documentos ou limitação de requisições. O app continua sendo uma demonstração
local com um PDF compartilhado. O exemplo `examples/app_openai.py` não utiliza
esses guardrails.

## Validação

```bash
python -m unittest discover -s tests -v
```

Os testes usam respostas simuladas e verificam os bloqueios e a ordem das chamadas.
Não medem a resistência real do Gemini a ataques nem consomem a cota da API.

Referência: [OWASP — LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).
