import pandas as pd
import json
import plotly.express as px

df = pd.read_json("ais_position.json")

fig = px.scatter_map(df, lat="lat", lon="lon", color="NavigationalStatus",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)

fig.show()