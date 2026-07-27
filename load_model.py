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