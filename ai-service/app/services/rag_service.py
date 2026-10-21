from app.schemas.chat import ChatMessage

from app.services.database_retrieval_service import (
    DatabaseRetrievalService
)

from app.services.llm_service import (
    LLMService
)


class RagService:

    def __init__(self):

        self.retriever = (
            DatabaseRetrievalService()
        )

        self.llm_service = (
            LLMService()
        )


    def _build_context(
        self,
        results: list[dict]
    ):

        context_blocks = []

        sources = []

        for rank, result in enumerate(
            results,
            start=1
        ):

            metadata = (
                result.get("metadata")
                or {}
            )

            document_name = (
                metadata.get(
                    "document_name",
                    "unknown"
                )
            )

            chunk_index = (
                result["chunk_index"]
            )

            score = (
                result["score"]
            )

            content = (
                result["content"]
            )


            context_blocks.append(
                f"""
[S{rank}]
Source: {document_name}
Chunk: {chunk_index}

{content}
""".strip()
            )


            sources.append(
                {
                    "rank": rank,
                    "document_name":
                        document_name,

                    "chunk_index":
                        chunk_index,

                    "score":
                        float(score),

                    "content":
                        content
                }
            )


        context = "\n\n".join(
            context_blocks
        )


        return context, sources


    def answer(
        self,
        question: str,
        top_k: int = 3,
        temperature: float = 0.2
    ):

        results = self.retriever.search(
            query=question,
            top_k=top_k
        )


        if not results:

            return {
                "answer":
                    "当前知识库中没有检索到相关资料。",

                "sources": []
            }


        context, sources = (
            self._build_context(
                results
            )
        )


        prompt = f"""
你正在执行基于企业知识库的问答任务。

请严格遵守以下规则：

1. 仅根据“检索证据”回答问题。
2. 不要使用检索证据之外的信息补充事实。
3. 如果证据不足，请明确回答：
   “根据当前知识库无法确定。”
4. 关键结论后使用 [S1]、[S2] 等方式标注证据来源。
5. 不要编造不存在的来源编号。
6. 回答应简洁、清晰。

====================
检索证据
====================

{context}

====================
用户问题
====================

{question}
""".strip()


        messages = [
            ChatMessage(
                role="user",
                content=prompt
            )
        ]


        answer = self.llm_service.chat(
            messages=messages,
            temperature=temperature
        )


        return {
            "answer": answer,
            "sources": sources
        }