from app.core.database import (
    get_connection
)


with get_connection() as connection:

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT version();"
        )

        version = cursor.fetchone()

        print(
            "PostgreSQL:",
            version[0]
        )


        cursor.execute(
            """
            SELECT extname
            FROM pg_extension
            WHERE extname = 'vector';
            """
        )

        extension = cursor.fetchone()

        print(
            "pgvector:",
            extension
        )