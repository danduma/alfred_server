from post_storage import PostsStore
import plac

posts_store = PostsStore(vector_dir="db")


def main(start_at=0):
    posts_store.import_lens_posts("data/bq-results-20230513-012625-1683941205838.csv", start_at=start_at)


if __name__ == '__main__':
    plac.call(main)
