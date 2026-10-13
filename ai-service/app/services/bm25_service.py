import json
from pathlib import Path

from rank_bm25 import BM25Okapi



class BM25Service:


    def __init__(self):

        data_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "data"
            / "network_documents.json"
        )


        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.documents = json.load(f)



        texts = [
            doc["content"]
            for doc in self.documents
        ]


        tokenized_docs = [
            list(text)
            for text in texts
        ]


        self.bm25 = BM25Okapi(
            tokenized_docs
        )



    def search(
        self,
        query,
        top_k=3
    ):


        tokens = list(query)


        scores = (
            self.bm25
            .get_scores(tokens)
        )


        ranked = sorted(
            enumerate(scores),
            key=lambda x:x[1],
            reverse=True
        )



        results=[]


        for index,score in ranked[:top_k]:

            document = (
                self.documents[index]
            )


            results.append(
                {
                    "id":
                        document["id"],

                    "content":
                        document["content"],

                    "score":
                        float(score),

                    "metadata":
                        {
                            "source":
                                "bm25"
                        }
                }
            )


        return results