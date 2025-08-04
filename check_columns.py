import pandas as pd

stream_df = pd.read_csv("data/streaming_availability.csv")
print(stream_df.columns.tolist())
