import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("Aachen_Barbershop_Reviews.csv")

# print(data.columns)

# print(data["user_num_reviews"].value_counts())

# print(data["user_is_local_guide"].value_counts())

# print(data["user_review_date"].value_counts())

na_data = data[data["user_review_description_original"].isna()].copy()

na_data["user_num_photos"].value_counts().plot(kind="bar")
plt.show()
