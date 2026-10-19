"""
Creates 500 fake animal records in my local MongoDB (database "aac",
collection "animals") so I can test the dashboard.

I no longer have the original Austin Animal Center dataset, so this script
makes up records that use the same field names and the same column order.
The order is important because the map callback gets the breed, name,
latitude and longitude by column number (4, 9, 13 and 14).

Usage:
    python seed_data.py
"""
import random
from datetime import datetime, timedelta

from mongo import AnimalShelter

RECORD_COUNT = 500
SEED = 499  # using the same seed gives us the same data every time we run it

# All the breeds used in the rescue filters, plus a few extra ones
DOG_BREEDS = [
    "Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland",
    "German Shepherd", "Alaskan Malamute", "Old English Sheepdog",
    "Siberian Husky", "Rottweiler", "Doberman Pinscher", "Golden Retriever",
    "Bloodhound", "Pit Bull Mix", "Chihuahua Shorthair Mix", "Beagle",
]
CAT_BREEDS = ["Domestic Shorthair Mix", "Domestic Medium Hair", "Siamese Mix"]
NAMES = [
    "Max", "Bella", "Lucy", "Rex", "Daisy", "Buddy", "Luna", "Rocky", "Molly",
    "Duke", "Sadie", "Bear", "Maggie", "Zeus", "Ruby", "Cooper", "Penny",
]
SEXES = ["Intact Female", "Intact Male", "Spayed Female", "Neutered Male"]
COLORS = ["Black", "Brown/White", "Tan", "Black/Tan", "White", "Tricolor"]
OUTCOMES = ["Adoption", "Transfer", "Return to Owner", "Euthanasia"]


def age_text(weeks):
    """Writes the age like the AAC data does, for example '2 years'."""
    if weeks >= 52:
        years = int(weeks // 52)
        return f"{years} year" + ("s" if years > 1 else "")
    months = max(1, int(weeks // 4))
    return f"{months} month" + ("s" if months > 1 else "")


def make_record(rng, rec_num, animal_id):
    animal_type = "Dog" if rng.random() < 0.85 else "Cat"
    breed = rng.choice(DOG_BREEDS if animal_type == "Dog" else CAT_BREEDS)
    # Half of the animals are between 6 months and 3 years old, which is the
    # age the rescue filters look for. Without this some filters had almost no results.
    if rng.random() < 0.5:
        weeks = round(rng.uniform(26, 156), 6)
    else:
        weeks = round(rng.uniform(4, 400), 6)
    outcome_time = datetime(2015, 1, 1) + timedelta(minutes=rng.randint(0, 3 * 525600))
    birth = outcome_time - timedelta(weeks=weeks)
    # Some animals in the real data have no name, so we leave about 5% empty
    name = "" if rng.random() < 0.05 else rng.choice(NAMES)

    # Keep the fields in the same order as the original dataset
    return {
        "rec_num": rec_num,
        "age_upon_outcome": age_text(weeks),
        "animal_id": animal_id,
        "animal_type": animal_type,
        "breed": breed,
        "color": rng.choice(COLORS),
        "date_of_birth": birth.strftime("%Y-%m-%d"),
        "datetime": outcome_time.strftime("%Y-%m-%d %H:%M:%S"),
        "monthyear": outcome_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "name": name,
        "outcome_subtype": "",
        "outcome_type": rng.choice(OUTCOMES),
        "sex_upon_outcome": rng.choice(SEXES),
        # Random locations around Austin, TX
        "location_lat": round(rng.uniform(30.2, 30.8), 6),
        "location_long": round(rng.uniform(-97.9, -97.3), 6),
        "age_upon_outcome_in_weeks": weeks,
    }


def generate_records(count=RECORD_COUNT, seed=SEED):
    rng = random.Random(seed)
    ids = rng.sample(range(600000, 800000), count)
    records = []
    for i in range(count):
        # In the real data the same animal can show up more than once, so
        # about 2% of the records reuse an ID we already created. This also
        # lets us test that the search returns all of the duplicates.
        if i > 0 and rng.random() < 0.02:
            animal_id = records[rng.randrange(i)]["animal_id"]
        else:
            animal_id = f"A{ids[i]}"
        records.append(make_record(rng, i + 1, animal_id))
    return records


if __name__ == "__main__":
    shelter = AnimalShelter()
    # Delete the old records first so we do not get duplicates if we run this again
    shelter.delete({}, many=True)
    for record in generate_records():
        shelter.create(record)
    print(f"Inserted {len(shelter.read({}))} synthetic records into aac.animals")
