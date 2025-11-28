from langsmith import Client

user_run_ids = ["3c30c498-969b-401d-bf07-a8e08a6a662b"]

client = Client()
for run_id in user_run_ids:
    try:
        client.run(run_id)
    except Exception as e:
        print(f"Failed to delete run {run_id}: {e}")

        continue
