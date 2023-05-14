from post_storage import PostsStore

posts_store = PostsStore(vector_dir="db")


def main():
    # posts_store.vectordb.
    # res = posts_store.search_posts("people who hate high blockchain fees")
    res = posts_store.search_posts("hottest artists in the world")
    for r in res:
        print(r.metadata)
        print(r.page_content)
        print("-----")


if __name__ == '__main__':
    main()


