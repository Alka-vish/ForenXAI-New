from datasets import load_dataset

dataset = load_dataset(
    "TheKernel01/Tiny-GenImage",
    split="train"
)

dataset.save_to_disk("../data/tiny-genimage-train")