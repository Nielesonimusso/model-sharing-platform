import sys

BACKEND = 'backend'
GATEWAY = 'gateway'
INGREDIENT_SERVICE = 'ingredient_service'
DATA_GATEWAY = 'data_access_gateway'


def print_usage():
    print(f'Usage: python {sys.argv[0]} <application name> [--test]')
    print(f'Applications: {GATEWAY} or {BACKEND} or {INGREDIENT_SERVICE} or {DATA_GATEWAY}')


def __is_test():
    return len(sys.argv) > 2 and sys.argv[2] == '--test'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        exit(0)

    if sys.argv[1] == BACKEND:
        from model_sharing_backend.run import run_backend

        run_backend()

    elif sys.argv[1] == GATEWAY:
        from model_access_gateway.run import run_gateway

        run_gateway()

    elif sys.argv[1] == INGREDIENT_SERVICE:
        from ingredient_data_service.run import run_ingredient_service

        run_ingredient_service()

    elif sys.argv[1] == DATA_GATEWAY:
        from data_access_gateway.run import run_data_access_gateway

        run_data_access_gateway()

    else:
        print_usage()
