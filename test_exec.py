from app.services.executor import run_data_collection_script

script = """
import pandas as pd
df = pd.DataFrame({"x":[1,2,3]})
df.to_csv("out.csv", index=False)
print("done!")
"""

print(run_data_collection_script(script))
