class ChunkingService:

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> list[str]:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be positive"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller "
                "than chunk_size"
            )

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = (
                end - chunk_overlap
            )

        return chunks
    def chunk_by_paragraph(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> list[str]:

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        chunks = []

        current = ""

        for paragraph in paragraphs:

            candidate = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) <= chunk_size:

                current = candidate

            else:

                if current:
                    chunks.append(
                        current.strip()
                    )

                if len(paragraph) > chunk_size:

                    long_chunks = self.chunk_text(
                        paragraph,
                        chunk_size,
                        chunk_overlap
                    )

                    chunks.extend(
                        long_chunks[:-1]
                    )

                    current = (
                        long_chunks[-1]
                        if long_chunks
                        else ""
                    )

                else:

                    current = paragraph

        if current:
            chunks.append(
                current.strip()
            )

        return chunks

    def chunk_markdown(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> list[str]:

        sections = []

        current_lines = []

        for line in text.splitlines():

            if (
                line.startswith("#")
                and current_lines
            ):

                sections.append(
                    "\n".join(
                        current_lines
                    ).strip()
                )

                current_lines = []

            current_lines.append(line)

        if current_lines:

            sections.append(
                "\n".join(
                    current_lines
                ).strip()
            )

        chunks = []

        for section in sections:

            if len(section) <= chunk_size:

                chunks.append(section)

            else:

                chunks.extend(
                    self.chunk_by_paragraph(
                        section,
                        chunk_size,
                        chunk_overlap
                    )
                )

        return chunks