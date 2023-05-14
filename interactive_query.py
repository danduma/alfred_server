from langchain.llms import OpenAI
from langchain.chains import VectorDBQA
from post_storage import PostsStore

posts_store = PostsStore(vector_dir="db")

def main():
    # qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=j.vectordb)

    while True:
        question = input("Question: ")

        res = posts_store.search_posts(question)
        for r in res:
            print(r.metadata)
            print(r.page_content)
            print("-----")

if __name__ == '__main__':
    main()