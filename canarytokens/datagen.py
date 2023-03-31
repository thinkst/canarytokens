from faker import Faker

fake = Faker()


def generate_person() -> dict[str, str]:
    address = fake.address()
    billing_zip = address.split(" ")[-1]
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "address": address,
        "billing_zip": billing_zip,
    }
