# Post Recommender Service

Сервис рекомендаций постов.

Проект реализует FastAPI-сервис, который по `user_id`, времени запроса и лимиту возвращает список рекомендованных постов.
Для пользователей используется разделение на группы A/B-теста: `control` и `test`. Для каждой группы загружается отдельная CatBoost-модель.

## Стек

- Python
- FastAPI
- CatBoost
- Pandas
- NumPy
- Scikit-learn
- PostgreSQL / CSV
- Jupyter Notebook

## Как скачать datasets/ — обязательно для запуска

Датасеты не хранятся в репозитории из-за размера — они выложены в разделе [Releases](https://github.com/tJoik/post_recommendation_service/releases/tag/v1.0-data), название архива для загрузки — datasets.zip.

3 команды для терминала — скачают архив, распакуют и удалят ненужное, выполнять из корня проекта:

```powershell
Invoke-WebRequest -Uri "https://github.com/tJoik/post_recommendation_service/releases/download/v1.0-data/datasets.zip" -OutFile datasets.zip
Expand-Archive datasets.zip -DestinationPath .
Remove-Item datasets.zip
```

Архив распаковывается в корень проекта — папка `datasets/` уже внутри datasets.zip, создавать её вручную в корне не нужно.

Должно получиться так:

```text
post_recommendation_service/
├── datasets/
│   ├── feed_data_df_with_target.csv
│   ├── feed_data_df.csv
│   ├── post_text_df.csv
│   └── user_data_df.csv
├── embeddings/
└── models/
```

## Как запустить проект

Создать виртуальное окружение:

```powershell
python -m venv venv
```

Активировать окружение:

```powershell
.\venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
python -m pip install -r requirements.txt
```

Запустить сервис:

```powershell
uvicorn app:app
```

## Пример запроса

```text
GET http://127.0.0.1:8000/post/recommendations/?id=200&time=2022-10-27T16:29:12&limit=5
```

Пример ответа:

```json
{
    "exp_group": "control",
    "recommendations": [
        {
            "id": 7298,
            "text": "I used to watch this show when I was a little girl. When I think about it, I only remember it vaguely. If you ask me, it was a good show. Two things I remember vaguely are the opening sequence and theme song. In addition to that, everyone was ideally cast. Also, the writing was very strong. The performances were top-grade, too. I hope some network brings it back so I can see every episode. Before I wrap this up, Id like to say that Ill always remember this show in my memory forever, even though I dont think Ive seen every episode. Now, in conclusion, if some network ever brings it back, I hope that you catch it one day before it goes off the air for good.",
            "topic": "movie"
        },
        {
            "id": 7319,
            "text": "Piece of subtle art. Maybe a masterpiece. Doubtlessly a special story about the ambiguity of existence. Tale in Kafka style about impossibility of victory or surviving in a perpetual strange world. The life is, in this film, only exercise of adaptation. Lesson about limits and original sin, about the frailty of innocence and error of his ways.Leopold Kessle is another Joseph K. Images of Trial and same ambiguous woman. And Europa is symbol of basic crisis who has many aspects like chimeric wars or unavailing search of truth/essence/golden age.Methaphor or parable, the movie is history of disappointeds evolution. War, peace, business or lie are only details of gelatin-time. Hypocrisy is a mask. Love- a convention. The sacrifice- only method to hope understanding a painful reality.",
            "topic": "movie"
        },
        {
            "id": 7318,
            "text": "The version I saw of this film was the Blockbuster rental with a similar title, but a swear word in it.This film was funny as hell. It was also true to the bone. If you have ever spent time in Hollywood or the area around it, you will understand the humor. If not, you may not get it at all.The story of two people in the business struggling to make it until they finally reach a breaking point, it is a rare gem. It states it is a drama, but it is a drama as much as Deer Hunter is a comedy.Loren Dean is wonderful, as always, as a supporting actor. Jamie Kennedy was able to hold his own well. His performance is especically impressive during the poodle scene. The only downside was Carmen Electra but we cant have everything.",
            "topic": "movie"
        },
        {
            "id": 7317,
            "text": "I cant believe this film was allowed to be made. These people should be drug out and beat with blunt objects. They should be tortured. This film is an abomination.Its nothing but footage from the first film. Whatever is original is freaky and makes no sense whatsoever. Its like some sort of drug hallucination.Like, whats with the laying on a mirror naked therapy. Also, whatever moron patched together this turd didnt even bother to watch the first film, because they kept calling Suzanna Loves character Natalie, when its Lacey. I felt like shouting that at the screen, ITS LACEY, ITS LACEY!!!!. I give it a -50 out of 10. MY GOD!!!!",
            "topic": "movie"
        },
        {
            "id": 7316,
            "text": "I give this movie 2 stars purely because of its slightly liberal plot line. Without going into too much detail.The acting in this movie is terrible. Really terrible - wooden, shallow.The graffiti on show is weak, so bloody weak that I can only wonder why they bothered to use graffiti artists at all. IT was obvious in the spraying scenes that theyd gotten other people in to do the work. They might as well have let the actors do the painting and saved themselves a few cents.I would avoid this film at all costs.The kid loco soundtrack used to be something I listened to on my iPod, its going to be a while before I can go back there for fear of this movie coming back into my mind.Avoid at all costs. Unless you are thinking to yourself Wow, its been a while since Ive seen a really sh*t movie....",
            "topic": "movie"
        }
    ]
}
```

## Описание моделей

В проекте используются две CatBoost-модели:

- `catboost_control.cbm` — модель для контрольной группы
- `catboost_test.cbm` — модель для тестовой группы

Для тестовой модели дополнительно используются эмбеддинги текстов постов.

## Ноутбуки

В папке `notebooks/` находятся 2 ноутбука: 1.) dev_rec_model.ipynb с подготовкой данных и обучением моделей 2.) ab_tests.ipynb с A/B-тестами.

## Важно

Доступ к PostgreSQL-БД скрыт.
Ноутбук dev_rec_model.ipynb, где производится загрузка из БД, воспроизводится целиком корректно только при наличии необходимых параметров подключения к БД Karpov.courses.
Для работы сервиса вне LMS Karpov.courses (локально) используются подготовленные CSV-файлы и сохранённые модели, без обращения к БД.