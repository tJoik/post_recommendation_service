import hashlib
import os
from typing import List
from fastapi import FastAPI
from schema import PostGet, Response
from datetime import datetime
from catboost import CatBoostClassifier
import pandas as pd
from sqlalchemy import create_engine


def get_model_path(path: str, lms_name: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально (нужно для LMS)
        MODEL_PATH = f'/workdir/user_input/{lms_name}'
    else:
        MODEL_PATH = path
    return MODEL_PATH

def load_models():
    model_path_test = get_model_path("models/catboost_test.cbm", "model_test")
    model_path_control = get_model_path("models/catboost_control.cbm", "model_control")

    catboost_test = CatBoostClassifier()
    catboost_control = CatBoostClassifier()

    catboost_test.load_model(model_path_test)
    catboost_control.load_model(model_path_control)

    return catboost_test, catboost_control

def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(
        "postgresql://USER:PASSWORD@HOST:PORT/DB_NAME"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

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

salt = '0_salt'
split_percentage = 50
def get_group(user_id: int) -> str:
    value = int(hashlib.md5((str(user_id) + salt).encode()).hexdigest(), 16) % 100
    if value < split_percentage:
        return 'control'
    return 'test'

def load_features_local():
    feed_data_df = pd.read_csv('datasets/feed_data_df.csv')
    post_text_df = pd.read_csv('datasets/post_text_df.csv')
    user_data_df = pd.read_csv('datasets/user_data_df.csv')
    return feed_data_df, post_text_df, user_data_df

def recommended_posts_control(id: int, time: datetime, limit: int = 5) -> List[PostGet]:
    selected_user = user_data_df[user_data_df['user_id'] == id]
    user_posts = post_text_df.drop('text', axis=1).assign(**selected_user.iloc[0].to_dict())
    user_posts = user_posts[['user_id', 'post_id', 'gender', 'age', 'country', 'city', 'os', 'source',
                             'exp_group_1', 'exp_group_2', 'exp_group_3', 'exp_group_4', 'topic']]
    mask = (feed_data_df['user_id'] == id) & (feed_data_df['timestamp'] < time)
    seen_ids = feed_data_df.loc[mask, 'post_id'].to_numpy()
    user_posts = user_posts[~user_posts['post_id'].isin(seen_ids)]
    user_posts = user_posts.copy()
    user_posts['pred_proba'] = catboost_control.predict_proba(user_posts.drop(columns=['user_id', 'post_id']))[:, 1]
    user_posts = user_posts.sort_values("pred_proba", ascending=False)
    user_posts = user_posts.head(limit)
    user_posts = user_posts.merge(
        post_text_df[['post_id', 'text']],
        on='post_id',
        how='left'
    )
    user_posts = user_posts.rename(columns={'post_id': 'id'})
    top_limit_posts = user_posts[['id', 'text', 'topic']]
    return top_limit_posts.to_dict(orient='records')

def recommended_posts_test(id: int, time: datetime, limit: int = 5) -> List[PostGet]:
    selected_user = user_data_df[user_data_df['user_id'] == id]
    user_posts = post_text_df.drop('text', axis=1).assign(**selected_user.iloc[0].to_dict())
    emb_cols = [str(i) for i in range(30)]
    user_posts = user_posts[['user_id', 'post_id', 'gender', 'age', 'country', 'city', 'os', 'source',
                             'exp_group_1', 'exp_group_2', 'exp_group_3', 'exp_group_4', 'topic'] + emb_cols]
    mask = (feed_data_df['user_id'] == id) & (feed_data_df['timestamp'] < time)
    seen_ids = feed_data_df.loc[mask, 'post_id'].to_numpy()
    user_posts = user_posts[~user_posts['post_id'].isin(seen_ids)]
    user_posts = user_posts.copy()
    user_posts['pred_proba'] = catboost_test.predict_proba(user_posts.drop(columns=['user_id', 'post_id']))[:, 1]
    user_posts = user_posts.sort_values("pred_proba", ascending=False)
    user_posts = user_posts.head(limit)
    user_posts = user_posts.merge(
        post_text_df[['post_id', 'text']],
        on='post_id',
        how='left'
    )
    user_posts = user_posts.rename(columns={'post_id': 'id'})
    top_limit_posts = user_posts[['id', 'text', 'topic']]
    return top_limit_posts.to_dict(orient='records')


app = FastAPI()
catboost_test, catboost_control = load_models()

if os.environ.get("IS_LMS") == "1":
    feed_data_df = load_features_feed()
    post_text_df = load_features_posts()
    user_data_df = load_features_user()
else:
    feed_data_df, post_text_df, user_data_df = load_features_local()
feed_data_df['timestamp'] = pd.to_datetime(feed_data_df['timestamp'])


@app.get("/post/recommendations/", response_model=Response)
def recommended_posts(id: int, time: datetime, limit: int = 5):
    group = get_group(id)
    print(f'user_id = {id}, group = {group}')
    if group == 'control':
        return {
            'exp_group': group,
            'recommendations': recommended_posts_control(id, time, limit)
                }
    elif group == 'test':
        return {
            'exp_group': group,
            'recommendations': recommended_posts_test(id, time, limit)
        }
    else:
        raise ValueError('unknown group')