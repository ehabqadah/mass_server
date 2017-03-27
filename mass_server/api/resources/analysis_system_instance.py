from flask import jsonify
from flask_modular_auth import privilege_required, RolePrivilege, AuthenticatedPrivilege, current_authenticated_entity

from mass_server.core.models import AnalysisSystemInstance, ScheduledAnalysis, User
from mass_server.api.config import api_blueprint
from mass_server.api.schemas import AnalysisSystemInstanceSchema, ScheduledAnalysisSchema
from mass_server.api.utils import get_pagination_compatible_schema, register_api_endpoint
from .base import BaseResource


class AnalysisSystemInstanceResource(BaseResource):
    schema = AnalysisSystemInstanceSchema()
    pagination_schema = get_pagination_compatible_schema(AnalysisSystemInstanceSchema)
    queryset = AnalysisSystemInstance.objects
    query_key_field = 'uuid'
    filter_parameters = []

    @privilege_required(AuthenticatedPrivilege())
    def get_list(self):
        """
        ---
        get:
            description: Get a list of all analysis system instances.
            responses:
                200:
                    description: A list of analysis system instances is returned.
                    schema: AnalysisSystemInstanceSchema
        """
        return super(AnalysisSystemInstanceResource, self).get_list()

    @privilege_required(AuthenticatedPrivilege())
    def get_detail(self, **kwargs):
        """
        ---
        get:
            description: Get a single analysis system instance object
            parameters:
                - in: path
                  name: uuid
                  type: string
            responses:
                200:
                    description: The analysis system instance is returned.
                    schema: AnalysisSystemInstanceSchema
                404:
                    description: No analysis system instance with the specified uuid has been found.
        """
        return super(AnalysisSystemInstanceResource, self).get_detail(**kwargs)

    @privilege_required(RolePrivilege('admin'))
    def post(self):
        """
        ---
        post:
            description: Create a new analysis system instance
            parameters:
                - in: body
                  name: body
                  schema: AnalysisSystemInstanceSchema
            responses:
                201:
                    description: The object has been created. The reply contains the newly created object.
                    schema: AnalysisSystemInstanceSchema
                400:
                    description: The server was not able to create an object based on the request data.
        """
        return super(AnalysisSystemInstanceResource, self).post()

    @privilege_required(RolePrivilege('admin'))
    def put(self, **kwargs):
        """
        ---
        put:
            description: Update an existing analysis system instance object
            parameters:
                - in: path
                  name: uuid
                  type: string
                - in: body
                  name: body
                  schema: AnalysisSystemInstanceSchema
            responses:
                200:
                    description: The object has been updated. The reply contains the updated object.
                    schema: AnalysisSystemInstanceSchema
                400:
                    description: The server was not able to update an object based on the request data.
                404:
                    description: No analysis system with the specified uuid has been found.
        """
        return super(AnalysisSystemInstanceResource, self).put(**kwargs)

    @privilege_required(RolePrivilege('admin'))
    def delete(self, **kwargs):
        """
        ---
        delete:
            description: Delete an existing analysis system instance object
            parameters:
                - in: path
                  name: uuid
                  type: string
            responses:
                204:
                    description: The object has been deleted.
                400:
                    description: The server was not able to delete an object based on the request data.
                404:
                    description: No analysis system instance with the specified uuid has been found.
        """
        return super(AnalysisSystemInstanceResource, self).delete(**kwargs)

    @privilege_required(RolePrivilege('admin'), RolePrivilege('analysis_system_instance'))
    def scheduled_analyses(self, **kwargs):
        """
        ---
        get:
            description: Get the scheduled analyses of a specific analysis system instance object
            parameters:
                - in: path
                  name: uuid
                  type: string
            responses:
                200:
                    description: The list of scheduled analyses is returned.
                    schema: ScheduledAnalysisSchema
                404:
                    description: No analysis system instance with the specified uuid has been found.
        """
        if kwargs['uuid'] is None:
            return jsonify({'error': 'Parameter \'{}\' must be specified'.format(self.query_key_field)}), 400
        elif (isinstance(current_authenticated_entity._get_current_object(), AnalysisSystemInstance) and current_authenticated_entity.uuid == kwargs['uuid']) \
            or (isinstance(current_authenticated_entity._get_current_object(), User) and current_authenticated_entity.is_admin):
            analysis_system_instance = AnalysisSystemInstance.objects.get(uuid=kwargs['uuid'])
            if not analysis_system_instance:
                return jsonify({'error': 'No object with key \'{}\' found'.format(kwargs[self.query_key_field])}), 404
            analysis_system_instance.update_last_seen()
            scheduled_analyses = ScheduledAnalysis.objects(analysis_system_instance=analysis_system_instance)
            serialized_result = ScheduledAnalysisSchema(many=True).dump(scheduled_analyses)
            return jsonify({
                'results': serialized_result.data,
            })
        else:
            return jsonify({'error': 'Analysis instance  \'{}\' not found'.format(kwargs[self.query_key_field])}), 404


register_api_endpoint('analysis_system_instance', AnalysisSystemInstanceResource)

api_blueprint.add_url_rule('/analysis_system_instance/<uuid>/scheduled_analyses/', view_func=AnalysisSystemInstanceResource().scheduled_analyses, methods=['GET'])
api_blueprint.apispec.add_path('/analysis_system_instance/{uuid}/scheduled_analyses/', view=AnalysisSystemInstanceResource.scheduled_analyses)
