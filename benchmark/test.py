import polars as pl

df = pl.read_csv("/home/ubuntu/codes/LLM4NetLab/results/0_summary/evaluation_summary.csv")
print(df.with_columns((pl.col("in_tokens") + pl.col("out_tokens")).alias("total_tokens")).select(["in_tokens"]).sum())
