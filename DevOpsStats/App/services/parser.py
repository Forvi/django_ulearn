import pandas as pd

from DevOpsStats.App.models import Profession


def main():
    print("start")
    df = pd.read_csv('vacancies_2024.csv', low_memory=False)
    print("end")
    keywords = [
        'devops', 'development operations'
    ]
    pattern = '|'.join(keywords)

    filtered_df = df[df['name'].str.contains(pattern, case=False, na=False)]
    filtered_df = filtered_df.dropna()
    objects = [Profession(**row) for index, row in filtered_df.iterrows()]

    Profession.objects.bulk_create(objects)