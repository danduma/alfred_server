import json
import pandas as pd
import torch.cuda
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from dotenv import load_dotenv
from tqdm import tqdm

import datetime

load_dotenv()


def adapt_metadata_chroma(metadata):
    """
    Given a metadata dictionary, adapt it to the format expected by chromadb.
    :param metadata:
    :return:
    """
    adapted_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, datetime.datetime):
            adapted_metadata[key] = value.timestamp()
        elif value is None:
            adapted_metadata[key] = ""
        else:
            adapted_metadata[key] = value
    return adapted_metadata


def documents_from_posts(entries):
    """
    Given a list of entries, create a list of documents.

    content,post_id,profile_id,main_content_focus,language,block_timestamp,content_uri
    :param entries:
    :return:
    """
    documents = []
    for entry in entries:
        metadata = adapt_metadata_chroma({"block_timestamp": entry['block_timestamp'],
                                          "post_id": entry['post_id'],
                                          "profile_id": entry['profile_id'],
                                          "main_content_focus": entry['main_content_focus'],
                                          "language": entry['language'],
                                          "content_uri": entry['content_uri']})

        documents.append(Document(page_content=entry['content'],
                                  metadata=metadata))
    return documents


def count_lines(filename):
    with open(filename, 'r') as file:
        line_count = 0
        for line in file:
            line_count += 1
    return line_count


class PostsStore:
    def __init__(self, vector_dir):
        if torch.cuda.is_available():
            args = {'device': 'cuda'}
        elif torch.has_mps:
            args = {'device': 'mps'}
        else:
            args = {'device': 'cpu'}

        self.embedding = SentenceTransformerEmbeddings(model_name="multi-qa-MiniLM-L6-cos-v1",
                                                       model_kwargs=args)
        self.vector_dir = vector_dir
        self.vectordb = Chroma(persist_directory=self.vector_dir,
                               embedding_function=self.embedding,
                               collection_name="journal")

    def import_lens_posts(self, filename, start_at=0):
        total_lines = count_lines(filename)

        # read csv file in chunks with pandas
        for chunk in tqdm(pd.read_csv(filename, chunksize=200), total=int(total_lines / 200)):
            if start_at > 0:
                start_at -= 1
                continue

            # convert chunk to json
            data = json.loads(chunk.to_json(orient="records"))
            # add chunk to collection
            documents = documents_from_posts(data)
            self.vectordb.add_documents(documents)
            # persist collection
            self.vectordb.persist()

    def search_posts(self, query, metadata={}, limit=10, fetch_k=50):
        # return self.vectordb.similarity_search_with_relevance_scores(query, k=limit)
        # return self.vectordb.search(query, "mmr", k=limit)

        if metadata:
            collection = self.vectordb._client.get_or_create_collection("journal")
            res = collection.query(query_texts=[query], where=metadata)
            zipped = zip(res['documents'][0], res['metadatas'][0])
            # Convert each tuple into a dictionary
            dicts = [dict(zip(['page_content', 'metadata'], tpl)) for tpl in zipped]

            documents = [Document(page_content=d['page_content'], metadata=d['metadata']) for d in dicts]
            return documents
        else:
            return self.vectordb.search(query, "mmr", k=limit, fetch_k=50, where=metadata)
