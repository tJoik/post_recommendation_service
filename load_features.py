def load_features_feed() -> pd.DataFrame:
    query = 'SELECT * FROM shigrav2_feed_data_df_m'
    feed_data_df = batch_load_sql(query)
    return feed_data_df

def load_features_posts() -> pd.DataFrame:
    query_1 = 'SELECT * FROM shigrav2_post_text_df_m'
    post_text_df = batch_load_sql(query_1)
    return post_text_df

def load_features_user() -> pd.DataFrame:
    query_1 = 'SELECT * FROM shigrav2_user_data_df_m'
    user_data_df = batch_load_sql(query_1)
    return user_data_df


def load_features_local():
    feed_data_df = pd.read_csv('datasets/feed_data_df.csv')
    post_text_df = pd.read_csv('datasets/post_text_df.csv')
    user_data_df = pd.read_csv('datasets/user_data_df.csv')
    return feed_data_df, post_text_df, user_data_df