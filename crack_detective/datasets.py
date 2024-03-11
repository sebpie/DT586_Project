import os
import pathlib

# Datasets are in the parent directory.
DataSourcePath = pathlib.Path(__file__).parent.parent.joinpath("Code_Images").resolve()
# "C:/Users/eid/Desktop/Code_Images/"


datasets = {}

def _add_dataset(name, *paths):
  global datasets
  datasets[name] = os.path.join(DataSourcePath, *paths )

_add_dataset('Asphalt', 'Asphalt/', '64')
_add_dataset('Asphalt_INV', 'Asphalt/', '64_INV/')
_add_dataset('Bridge', 'Bridge/', '64')
_add_dataset('Bridge_INV', 'Bridge', '64_INV')
_add_dataset('Mendelay_1', 'Mendelay_1', '64')
_add_dataset('Mendelay_1_INV', 'Mendelay_1', '64_INV')
_add_dataset('Mendelay_2', 'Mendelay_2', '64')
_add_dataset('Mendelay_2_INV', 'Mendelay_2', '64_INV')
_add_dataset('Private', 'Private', '64')
_add_dataset('Private', 'Private', 'INV')
_add_dataset('Mendelay_FULL', 'Mendelay_FULL')


if __name__ == "__main__":
    print(f"Data source: {DataSourcePath}")
    print(f"Datasets available:")
    for dataset in datasets:
        print(f"\t* {dataset}")