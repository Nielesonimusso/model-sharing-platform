from datetime import datetime

import bcrypt, uuid

from common_data_access.db_initialize import BaseDbInitialize
from .company import Company
from .food_product_models import FoodProduct, Ingredient, FoodProductProcessingStep, ProcessingStepProperty, FoodProductPermission
from .model_info import ModelInfo, ModelPermission, ModelPermissionTypes
from .simulation import Simulation
from .user import User
from .data_source_info import DataSourceInfo, DataSourcePermission, DataSourcePermissionTypes


class ModelDbInitialize(BaseDbInitialize):

    def _seed_database(self, **kwargs):
        #
        # COMPANIES
        #
        company_tue = Company(name='Technical University Eindhoven',
                              address='De Zaale, Eindhoven, The Netherlands').save()
        company_wur = Company(name='University Wageningen and Research',
                address='Droevendaalsesteeg 4, 6708 PB Wageningen, The Netherlands').save()
        company_unilever = Company(name='Unilever N.V.', address='Weena 455, 3013AL Rotterdam, The Netherlands').save()
        Company(name='Jheronimus Academy of Data Science',
                address='Sint Janssingel 92, 5211 DA \'s-Hertogenbosch, The Netherlands').save()
        company_nizo = Company(name='NIZO', address='Kernhemseweg 2, 6718 ZB Ede, The Netherlands').save()
        Company(name='Symrise', address='Holzminden, Germany').save()
        Company(name='Institute for Sustainable Process Technology',
                address='Groen van Prinstererlaan 37, 3818 JN Amersfoort, The Netherlands').save()
        company_lowmato = Company(name='LOWmato', address='De Zaale, Eindhoven, The Netherlands').save()
        Company(name='Unilever Food Testing', address='NL').save()
        Company(name='TUe AgriFoodTech', address='DE').save()

        #
        # USERS
        #
        password = b'inof1234'
        u1, u2, u3, u4, u5, u6 = 'hossain', 'niels', 'michiel', 'jakob', 'kevin', 'puneet'
        if User.query.filter(User.username == u1).count() == 0:
            user = User(username=u1, full_name='Hossain Muctadir', email='h.m.muctadir@tue.nl',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_lowmato, 
                        api_key=password.decode('utf-8')+u1)
            user.save()

        if User.query.filter(User.username == u2).count() == 0:
            user = User(username=u2, full_name='Niels Rood', email='n.rood@tue.nl',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_lowmato, 
                        api_key=password.decode('utf-8')+u2)
            user.save()

        if User.query.filter(User.username == u3).count() == 0:
            user = User(username=u3, full_name='Michiel Gribnau', email='michiel@unilever.com',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_unilever, 
                        api_key=password.decode('utf-8')+u3)
            user.save()

        if User.query.filter(User.username == u4).count() == 0:
            user = User(username=u4, full_name='Jakob de Vlieg', email='jakob@tue.nl',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_tue, 
                        api_key=password.decode('utf-8')+u4)
            user.save()

        if User.query.filter(User.username == u5).count() == 0:
            user = User(username=u5, full_name='Kevin van Koerten', email='kevin@nizo.nl',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_nizo, 
                        api_key=password.decode('utf-8')+u5)
            user.save()

        if User.query.filter(User.username == u6).count() == 0:
            user = User(username=u6, full_name='Puneet Mishra', email='puneet@wur.nl',
                        password_hash=bcrypt.hashpw(password, bcrypt.gensalt()), company=company_wur, 
                        api_key=password.decode('utf-8')+u6)
            user.save()

        #
        # FOOD PRODUCTS
        #
        # fp_ts_nl = FoodProduct(name='Tomato Soup NL', company_code='NL_TOM_SOUP', standard_code='STD_TOM_SOUP',
        #                        dosage=250,
        #                        dosage_unit="gram per litre", ingredients=
        #                        [Ingredient(company_code='10007', standard_code='10007', name='Tomaten standaard',
        #                                    amount=20,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10005', standard_code='10005', name='Salt', amount=3,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10003', standard_code='10003', name='Azijn 10%', amount=2,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10001', standard_code='10001', name='Sugar', amount=3,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10009', standard_code='10009', name='Water', amount=74,
        #                                    amount_unit='%')], processing_steps=
        #                        [FoodProductProcessingStep(name='Mixing', equipment='Mixer', properties=[
        #                            ProcessingStepProperty(name='Speed', value='50', unit='rpm')])],
        #                        created_on=datetime.utcnow(),
        #                        created_by=User.query.get_one_where(User.username == u1),
        #                        owner=company_tue).save()

        # fp_ts_de = FoodProduct(name='Tomato Soup DE', company_code='DE_TOM_SOUP', standard_code='STD2_TOM_SOUP',
        #                        dosage=250,
        #                        dosage_unit="gram per litre", ingredients=
        #                        [Ingredient(company_code='10007', standard_code='10007', name='Tomaten standaard',
        #                                    amount=20, amount_unit='%'),
        #                         Ingredient(company_code='10005', standard_code='10005', name='Salt', amount=3,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10003', standard_code='10003', name='Azijn 10%', amount=2,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10001', standard_code='10001', name='Sugar', amount=3,
        #                                    amount_unit='%'),
        #                         Ingredient(company_code='10009', standard_code='10009', name='Water', amount=74,
        #                                    amount_unit='%')], processing_steps=
        #                        [FoodProductProcessingStep(name='Mixing', equipment='Mixer', properties=[
        #                            ProcessingStepProperty(name='Speed', value='50', unit='rpm')])],
        #                        created_on=datetime.utcnow(),
        #                        created_by=User.query.get_one_where(User.username == u2), owner=company_unilever).save()

        # fp_ts_de.permissions.append(FoodProductPermission(company_id=company_tue.id, food_product_id=fp_ts_de.id))
        # fp_ts_de.save()

        # FoodProduct(name='Tomato Ketchup', company_code='TOM_KET_001', standard_code='TOM_KET_001',
        #             dosage=250, dosage_unit="gram per litre", ingredients=
        #             [Ingredient(company_code='10007', standard_code='10007', name='Tomato Sweet', amount=60,
        #                         amount_unit='%'),
        #              Ingredient(company_code='10005', standard_code='10005', name='Salt', amount=3, amount_unit='%'),
        #              Ingredient(company_code='10009', standard_code='10009', name='Water', amount=20, amount_unit='%'),
        #              Ingredient(company_code='10006', standard_code='10006', name='KCL', amount=2, amount_unit='%'),
        #              Ingredient(company_code='10001', standard_code='10001', name='Sugar', amount=20, amount_unit='%')],
        #             created_on=datetime.utcnow(), created_by=User.query.get_one_where(User.username == u2),
        #             owner=company_unilever).save()

        #
        # MODELS
        #
        # m1 = ModelInfo(name='Tomato soup sweetness and sourness model',
        #                description='This model calculates the sweetness and sourness of a tomato soup',
        #                price=10, gateway_url='http://sweet-sourness-model-access-gateway:5001', is_connected=True,
        #                owner=company_tue, created_on=datetime.utcnow(),
        #                created_by=User.query.get_one_where(User.username == u1),
        #                ontology_uri='http://www.foodvoc.org/resource/InternetOfFoodModel/tomatoSoupModel'
        #                ).save()

        # m2 = ModelInfo(name='Chicken soup taste model', description='This model calculates the taste of a chicken soup',
        #                price=21, gateway_url='http://tomato-saltiness-model-access-gateway:5003', is_connected=True,
        #                owner=company_unilever, created_on=datetime.utcnow(),
        #                created_by=User.query.get_one_where(User.username == u2),
        #                ontology_uri='http://www.foodvoc.org/resource/InternetOfFoodModel/tomatoSoupModel'
        #                ).save()

        # m3 = ModelInfo(name='Tomato soup saltiness and tomato taste model',
        #                description='This model calculates the saltiness and tomato taste of a tomato soup',
        #                price=10, gateway_url='http://tomato-saltiness-model-access-gateway:5001', is_connected=True,
        #                owner=company_unilever, created_on=datetime.utcnow(),
        #                created_by=User.query.get_one_where(User.username == u2),
        #                ontology_uri='http://www.foodvoc.org/resource/InternetOfFoodModel/tomatoSoupModel'
        #                ).save()

        # m3.permissions.append(ModelPermission(model_info_id=m3.id, company_id=company_tue.id,
        #                                       permission_type=ModelPermissionTypes.VIEW_AND_EXECUTE))
        # m3.save()

        # m4 = ModelInfo(name='Tomato soup nutrition information model',
        #                description='This model calculates the nutrition information of tomato soup',
        #                price=5, gateway_url='http://nutrition-model-access-gateway:5001', is_connected=True,
        #                owner=company_unilever, created_on=datetime.utcnow(),
        #                created_by=User.query.get_one_where(User.username == u2), 
        #                ontology_uri='http://www.foodvoc.org/resource/InternetOfFoodModel/tomatoSoupModel'
        #                ).save()

        # m4.permissions.append(ModelPermission(model_info_id=m4.id, company_id=company_tue.id,
        #                                       permission_type=ModelPermissionTypes.VIEW_AND_EXECUTE))
        # m4.save()

        # #
        # # SIMULATIONS
        # #
        # Simulation(name='Tomato Soup Saltiness and Sourness Simulation',
        #            food_product=fp_ts_nl, models=[m1],
        #            owner=company_tue, created_on=datetime.utcnow(),
        #            created_by=User.query.get_one_where(User.username == u1)).save()

        # Simulation(name='Tomato Soup Sweetness and Tomato Taste Simulation',
        #            food_product=fp_ts_de, models=[m2, m3],
        #            owner=company_unilever, created_on=datetime.utcnow(),
        #            created_by=User.query.get_one_where(User.username == u2)).save()
