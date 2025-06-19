def load_dataset():
    dataset_path = "/root/autodl-tmp/FinancialStrategy2Code/rl/data_rl/merged_strategy_dataset.json"
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    return dataset