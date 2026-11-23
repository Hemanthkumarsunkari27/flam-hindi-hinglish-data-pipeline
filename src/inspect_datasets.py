
from datasets import get_dataset_config_names, load_dataset

DATASETS = [
    "LingoIITGN/COMI-LINGUA",
    "LingoIITGN/HinGE"
]

for dataset_name in DATASETS:
    print("\n" + "=" * 60)
    print("DATASET:", dataset_name)

    try:
        configs = get_dataset_config_names(dataset_name)
        print("Available configurations:", configs)

        config = configs[0] if configs else None

        if config:
            dataset = load_dataset(
                dataset_name,
                config,
                split="train",
                streaming=True
            )
        else:
            dataset = load_dataset(
                dataset_name,
                split="train",
                streaming=True
            )

        first_record = next(iter(dataset))

        print("Available columns:", list(first_record.keys()))
        print("First record:")
        print(first_record)

    except Exception as error:
        print("Error:", error)
