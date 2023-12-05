import typer
from typing import TypedDict


class Map:
    def __init__(self, dest, src, range) -> None:
        self.dest_range_start = dest
        self.source_range_start = src
        self.range_length = range


class Mappings(TypedDict):
    seed_to_soil: list[Map]
    soil_to_fertilizer: list[Map]
    fertilizer_to_water: list[Map]
    water_to_light: list[Map]
    light_to_temperature: list[Map]
    temperature_to_humidity: list[Map]
    humidity_to_location: list[Map]


class SeedValues(TypedDict):
    seed: int
    soil: int
    fertilizer: int
    water: int
    light: int
    temperature: int
    humidity: int
    location: int


class Seed:
    def __init__(self, num) -> None:
        self.values: SeedValues = {}
        self.values["seed"] = num


def lookup(src: int, maps: list[Map]) -> int:
    for map in maps:
        if (
            src >= map.source_range_start
            and src < map.source_range_start + map.range_length
        ):
            return map.dest_range_start + (src - map.source_range_start)
    return src

def reverse_lookup(dest: int, maps: list[Map]) -> int:
    for map in maps:
        if (
            dest >= map.dest_range_start
            and dest < map.dest_range_start + map.range_length
        ):
            return map.source_range_start + (dest - map.dest_range_start)
    return dest


def find_seeds_part_1(input: list[str]) -> list[Seed]:
    seeds: list[Seed] = []
    for row in input:
        if row.startswith("seeds: "):
            seed_strs = row.split(":")[1].split(" ")
            seed_ints = [int(x) for x in seed_strs if x]
            for i in seed_ints:
                seed = Seed(i)
                seeds.append(seed)
            return seeds


def find_seed_ranges_part_2(input: list[str]) -> list[tuple[int, int]]:
    #seeds: list[Seed] = []
    seeds: list[tuple[int, int]] = []
    for row in input:
        if row.startswith("seeds: "):
            seed_strs = row.split(":")[1].split(" ")
            seed_ints = [int(x) for x in seed_strs if x]
            for start, num in zip(seed_ints[::2], seed_ints[1::2]):
                seeds.append((start, num))
                # for i in range(start, start + num):
                #     seed = Seed(i)
                #     seeds.append(seed)
            return seeds


def find_mappings(input: list[str]) -> Mappings:
    mappings = Mappings()
    for key in Mappings.__required_keys__:
        mappings[key] = []

    current_map_key = None
    for row in input:
        if row == "":
            continue
        elif " map:" in row:
            current_map_key = row.split(" ")[0].replace("-", "_")
        elif current_map_key is not None:
            try:
                map_strs = row.split(" ")
                map_ints = [int(x) for x in map_strs if x]
                if len(map_ints) != 3:
                    raise Exception(f"Error parsing row: {row}")
                map = Map(*map_ints)
                mappings[current_map_key].append(map)
            except Exception as e:
                print(f"Error parsing row: {row}")
                raise e
    return mappings


def resolve_seeds(seeds: list[Seed], mappings: Mappings) -> list[Seed]:
    for seed in seeds:
        next_key_startswith = "seed"
        for _ in mappings:
            for k in mappings:
                if k.startswith(next_key_startswith):
                    key = k
                    break
            source_key = key.split("_")[0]
            dest_key = key.split("_")[-1]
            next_key_startswith = dest_key
            seed.values[dest_key] = lookup(seed.values[source_key], mappings[key])
    return seeds

def resolve_seed_reverse(location: int, mappings: Mappings) -> Seed:
    seed = Seed(-1)
    seed.values["location"] = location
    next_key_endswith = "location"
    for _ in mappings:
        for k in mappings:
            if k.endswith(next_key_endswith):
                key = k
                break
        source_key = key.split("_")[0]
        dest_key = key.split("_")[-1]
        next_key_endswith = source_key
        seed.values[source_key] = reverse_lookup(seed.values[dest_key], mappings[key])
    return seed



def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    seeds = find_seeds_part_1(input)
    mappings = find_mappings(input)
    seeds = resolve_seeds(seeds, mappings)
    locations = [seed.values["location"] for seed in seeds]
    print(f"Min location part 1: {min(locations)}")

    seed_ranges = find_seed_ranges_part_2(input)
    mappings = find_mappings(input)
    #seeds = resolve_seeds(seeds, mappings)
    location = 0
    while True:
        seed = resolve_seed_reverse(location, mappings)
        #print(f"Resolved location {location} to seed {seed.values['seed']}")
        for start, num in seed_ranges:
            if seed.values["seed"] >= start and seed.values["seed"] < start + num:
                print(f"Location {location} is seed {seed.values['seed']}")
                return
        location+=1
    #locations = [seed.values["location"] for seed in seeds]
    #print(f"Min location part 2: {min(locations)}")


if __name__ == "__main__":
    typer.run(main)
