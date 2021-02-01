from sqlalchemy import or_
from werkzeug.exceptions import abort

from common_data_access.db_access import Query


class PermissionFilteredQuery(Query):

    def get_all_owned_by(self, company_id):
        return self.get_where(self._owner_condition(self._entity_with_owner_and_creator(), company_id))

    def get_all_created_by(self, user_id):
        return self.get_where(self._creator_condition(self._entity_with_owner_and_creator(), user_id))

    def get_all_accessible_by(self, company_id, *filter_criteria):
        entity = self._entity_with_owner_and_creator()
        q = self.filter(or_(self._owner_condition(entity, company_id),
                            entity.permissions.any(self._has_permission_condition(entity, company_id))),
                        *filter_criteria)
        return q.all()

    def get_one_owned_where_or_404(self, company_id, *criteria):
        return self.get_one_where_or_404(self._owner_condition(self._entity_with_owner_and_creator(), company_id),
                                         *criteria)

    def get_one_created_by_where_or_404(self, user_id, *criteria):
        return self.get_one_where_or_404(self._creator_condition(self._entity_with_owner_and_creator(), user_id),
                                         *criteria)

    def get_accessible_or_404(self, company_id, entity_id):
        entities = self.get_all_accessible_by(company_id, self._entity_with_owner_and_creator().id == entity_id)
        if len(entities) == 0:
            abort(404, description='not found')
        return entities[0]

    def get_created_by_or_404(self, user_id, entity_id):
        return self.get_one_created_by_where_or_404(user_id, self._mapper_zero().class_.id == entity_id)

    def get_owned_or_404(self, company_id, entity_id):
        return self.get_one_owned_where_or_404(company_id, self._mapper_zero().class_.id == entity_id)

    def _owner_condition(self, entity, owner_id):
        return entity.owner_id == owner_id

    def _creator_condition(self, entity, creator_id):
        return entity.created_by_id == creator_id

    # noinspection PyUnresolvedReferences
    def _has_permission_condition(self, entity, company_id):
        from model_sharing_backend.src.models.base_model import BasePermission
        if hasattr(entity, 'permissions') and issubclass(entity.permissions.property.entity.class_, BasePermission):
            return entity.permissions.property.entity.class_.company_id == company_id
        else:
            return entity.id == None # always false

    def _entity_with_owner_and_creator(self):
        from model_sharing_backend.src.models.base_model import BaseModelWithOwnerAndCreator
        mapped_class = self._mapper_zero().class_
        if issubclass(mapped_class, BaseModelWithOwnerAndCreator):
            return mapped_class
        else:
            raise Exception(f'cannot query for owner. '
                            f'{mapped_class.__name__} is not a subclass of {BaseModelWithOwnerAndCreator.__name__}')
