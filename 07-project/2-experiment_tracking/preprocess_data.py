import argparse
import os
import pickle
import spacy
import pandas as pd
from sklearn.model_selection import train_test_split

nlp = spacy.load("en_core_web_md")

def dump_pickle(obj, filename):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

def preprocess(df: pd.DataFrame, nlp: nlp):
    df['vector'] = df.title.apply(lambda x: nlp(x).vector)
    return df

def run(raw_data_path: str, dest_path: str, dataset: str = "green"):
    # load parquet files
    df_true = pd.read_csv("../data/True.csv")
    df_fake = pd.read_csv("../data/Fake.csv")

    df_true['label'] = 1
    df_fake['label'] = 0

    df_true = preprocess(df_true, nlp)
    df_fake = preprocess(df_fake, nlp)

    concat_data = pd.concat([df_true[['vector','label']],df_fake[['vector','label']]])
    concat_data = concat_data.sample(frac = 1)

    X_train, X_test, y_train, y_test = train_test_split(concat_data.vector, concat_data.label, test_size=0.1)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.12, random_state=1) # 0.25 x 0.8 = 0.2

    # save dictvectorizer and datasets
    dump_pickle((X_train, y_train),  "data_split/train.pkl")
    dump_pickle((X_valid, y_valid),  "data_split/valid.pkl")
    dump_pickle((X_test, y_test), "data_split/test.pkl")