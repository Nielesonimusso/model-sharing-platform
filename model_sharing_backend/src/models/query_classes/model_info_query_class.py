from sqlalchemy import and_, or_
from werkzeug.exceptions import abort

from .permission_query_class import PermissionFilteredQuery


class ModelInfoQuery(PermissionFilteredQuery):
    def get_all_executable_by(self, company_id, *filter_criteria):
        from model_sharing_backend.src.models.model_info import ModelPermissionTypes
        entity = self._entity_with_owner_and_creator()
        q = self.filter(or_(self._owner_condition(entity, company_id),
                            entity.permissions.any(
                                self._has_permission_condition(entity, company_id,
                                                               ModelPermissionTypes.VIEW_AND_EXECUTE))),
                        entity.is_connected, *filter_criteria)
        return q.all()

    def get_executable_or_404(self, company_id, model_id):
        entities = self.get_all_executable_by(company_id, self._entity_with_owner_and_creator().id == model_id)
        if len(entities) == 0:
            abort(404, description='not found')
        return entities[0]

    def _has_permission_condition(self, entity, company_id, permission_type=None, *additional_conditions):
        permission_entity = entity.permissions.property.entity.class_
        if permission_type is None:
            return permission_entity.company_id == company_id
        else:
            return and_(permission_entity.company_id == company_id,
                        permission_entity.permission_type == permission_type, *additional_conditions)
