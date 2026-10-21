import json

from app.core.database import (
    get_connection
)


class VectorStore:


    def create_document(
        self,
        file_name: str,
        file_type: str
    ) -> int:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO documents (
                        file_name,
                        file_type
                    )
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (
                        file_name,
                        file_type
                    )
                )

                document_id = (
                    cursor.fetchone()[0]
                )

            connection.commit()

        return document_id


    def add_chunks(
        self,
        document_id: int,
        chunks: list[dict]
    ):

        with get_connection() as connection:

            with connection.cursor() as cursor:

                for chunk in chunks:

                    cursor.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id,
                            chunk_index,
                            content,
                            metadata,
                            embedding
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        );
                        """,
                        (
                            document_id,

                            chunk[
                                "chunk_index"
                            ],

                            chunk[
                                "content"
                            ],

                            json.dumps({
                                "document_name":
                                    chunk[
                                        "document_name"
                                    ],

                                "document_type":
                                    chunk[
                                        "document_type"
                                    ],

                                "chunk_strategy":
                                    chunk[
                                        "chunk_strategy"
                                    ]
                            }),

                            chunk[
                                "embedding"
                            ]
                        )
                    )

            connection.commit()

    def similarity_search(
        self,
        query_embedding,
        top_k: int = 3
    ):

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        dc.id,
                        dc.document_id,
                        dc.chunk_index,
                        dc.content,
                        dc.metadata,

                        1 - (
                            dc.embedding <=> %s
                        ) AS score

                    FROM document_chunks dc

                    ORDER BY
                        dc.embedding <=> %s

                    LIMIT %s;
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        top_k
                    )
                )

                rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append(
                {
                    "id": row[0],
                    "document_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "metadata": row[4],
                    "score": float(
                        row[5]
                    )
                }
            )

        return results