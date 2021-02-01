from typing import List

from faker import Faker

__faker = Faker()


def create_simulation_dict(model_ids: List[str], product_id: str):
    return {
        "description": __faker.paragraph(),
        "food_product_id": product_id,
        "model_ids": model_ids,
        "name": __faker.sentence()
    }


def create_model_info_dict() -> dict:
    return {
        'description': __faker.sentence(),
        'is_connected': True,
        'name': __faker.sentence(),
        'price': __faker.pyfloat(positive=True),
        'gateway_url': 'http://localhost:5001/',
        'input_descriptions': [
            {
                'description': __faker.sentence(),
                'labels': [
                    {
                        'language': __faker.random_element(elements=('en', 'nl')),
                        'name': __faker.word()
                    },
                    {
                        'language': __faker.random_element(elements=('en', 'nl')),
                        'name': __faker.word()
                    }
                ],
                'unit': __faker.random_element(elements=('gram', 'kilogram', 'ounce'))
            } for _ in range(__faker.random_digit() + 1)
        ],
        'output_descriptions': [
            {
                'description': __faker.sentence(),
                'labels': [
                    {
                        'language': __faker.random_element(elements=('en', 'nl')),
                        'name': __faker.word()
                    }
                ],
                'unit': __faker.random_element(elements=('gram', 'kilogram', 'ounce'))
            } for _ in range(__faker.random_digit() + 1)
        ]
    }


def create_unilever_tomato_soup_model() -> dict:
    return {
        'description': __faker.sentence(),
        'is_connected': True,
        'name': 'tomato soup taste model',
        'price': __faker.pyfloat(positive=True),
        'gateway_url': 'http://localhost:5001/',
        'input_descriptions': [
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'product dosage'}],
                'unit': 'gram per litre'
            },
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'salt'}],
                'unit': 'percent'
            },
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'tomato standard'}],
                'unit': 'percent'
            },
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'vinegar 10%'}],
                'unit': 'percent'
            },
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'sugar'}],
                'unit': 'percent'
            },
            {
                'description': __faker.sentence(),
                'labels': [{'language': __faker.random_element(elements=('en', 'nl')), 'name': 'water'}],
                'unit': 'percent'
            },
        ],
        'output_descriptions': [
            {
                'description': __faker.sentence(),
                'labels': [
                    {
                        'language': __faker.random_element(elements=('en', 'nl')),
                        'name': __faker.word()
                    }
                ],
                'unit': __faker.random_element(elements=('gram', 'kilogram', 'ounce'))
            } for _ in range(__faker.random_digit() + 1)
        ]
    }


def create_unilever_tomato_soup_map() -> dict:
    food_product = create_food_product_map()
    food_product.update({
        'name': 'Tomato Soup',
        'dosage': 250,
        'dosage_unit': 'gram per litre',
        'ingredients': [
            {
                'company_code': '10007',
                'standard_code': '10007',
                'name': 'Tomato standard',
                'amount': 20,
                'amount_unit': '%'
            },
            {
                'company_code': '10005',
                'standard_code': '10005',
                'name': 'Salt',
                'amount': 4,
                'amount_unit': '%'
            },
            {
                'company_code': '10003',
                'standard_code': '10003',
                'name': 'Vinegar 10%',
                'amount': 0,
                'amount_unit': '%'
            },
            {
                'company_code': '10001',
                'standard_code': '10001',
                'name': 'Sugar',
                'amount': 2,
                'amount_unit': '%'
            },
            {
                'company_code': '10009',
                'standard_code': '10009',
                'name': 'Water',
                'amount': 74,
                'amount_unit': '%'
            }
        ]
    })
    return food_product


def create_unilever_tomato_soup_map_with_different_units() -> dict:
    food_product = create_food_product_map()
    food_product.update({
        'name': 'Tomato Soup',
        'dosage': 0.250,
        'dosage_unit': 'kilogram per litre',
        'ingredients': [
            {
                'company_code': '10007',
                'standard_code': '10007',
                'name': 'Tomato standard',
                'amount': 50,
                'amount_unit': 'gram per litre'
            },
            {
                'company_code': '10005',
                'standard_code': '10005',
                'name': 'Salt',
                'amount': 10,
                'amount_unit': 'gram per litre'
            },
            {
                'company_code': '10003',
                'standard_code': '10003',
                'name': 'Vinegar 10%',
                'amount': 0,
                'amount_unit': 'gram per litre'
            },
            {
                'company_code': '10001',
                'standard_code': '10001',
                'name': 'Sugar',
                'amount': 5,
                'amount_unit': 'gram per litre'
            },
            {
                'company_code': '10009',
                'standard_code': '10009',
                'name': 'Water',
                'amount': 185,
                'amount_unit': 'gram per litre'
            }
        ]
    })
    return food_product


def create_food_product_map() -> dict:
    return {
        'company_code': __faker.ssn(),
        # 'standard_code': __faker.ssn(),
        'dosage': __faker.pyfloat(),
        'dosage_unit': __faker.word(),
        'food_product_properties': [
            {
                'name': __faker.word(),
                'unit': __faker.word(),
                'method': __faker.word(),
                'value': __faker.pyfloat()
            } for _ in range(__faker.random_digit() + 1)
        ],
        'ingredients': [
            {
                'amount': __faker.pyint(),
                'amount_unit': __faker.word(),
                'company_code': __faker.ssn(),
                'standard_code': __faker.ssn(),
                'name': __faker.word()
            } for _ in range(__faker.random_digit() + 1)
        ],
        'name': __faker.sentence(),
        'packagings': [{
            'company_code': __faker.ssn(),
            'standard_code': __faker.ssn(),
            'name': __faker.sentence(),
            'shape': __faker.word(),
            'thickness': __faker.pyfloat(),
            'thickness_unit': __faker.word()
        } for _ in range(__faker.random_digit() + 1)],
        'processing_steps': [
            {
                'equipment': __faker.word(),
                'name': __faker.sentence(),
                'properties': [
                    {
                        'name': __faker.sentence(),
                        'unit': __faker.word(),
                        'value': __faker.pyfloat()
                    } for _ in range(__faker.random_digit() + 1)
                ]
            }
        ]
    }


def create_registration_dict(company_id):
    return {
        'full_name': __faker.name(),
        'username': __faker.user_name(),
        'password': __faker.password(),
        'email': __faker.email(),
        'company_id': company_id
    }


def create_login_dict(username=None, password=None):
    return {
        'username': username or __faker.user_name(),
        'password': password or __faker.password()
    }
