from flask import jsonify, request
from flask.views import MethodView
from mongoengine import DoesNotExist

from mass_server.core.utils import PaginationFunctions


class Ref(object):

    def __init__(self, key):
        self.key = key

    def resolve(self, obj):
        return getattr(obj, self.key, None)


class BaseResource(MethodView):
    schema = None
    pagination_schema = None
    queryset = None
    query_key_field = None
    filter_parameters = []

    @property
    def schema(self):
        return Ref('schema').resolve(self)

    @property
    def pagination_schema(self):
        return Ref('pagination_schema').resolve(self)

    @property
    def queryset(self):
        return Ref('queryset').resolve(self)

    @property
    def query_key_field(self):
        return Ref('query_key_field').resolve(self)

    @property
    def filter_parameters(self):
        return Ref('filter_parameters').resolve(self)

    @PaginationFunctions.paginate
    def _get_list(self):
        filter_condition = {}
        for parameter in self.filter_parameters:
            if parameter in request.args:
                filter_condition[parameter] = request.args[parameter]

        return self.queryset().filter(**filter_condition)

    def get_list(self):
        paginated_objects = self._get_list()
        result = self.pagination_schema.dump(paginated_objects)
        return jsonify(result.data)

    def get_detail(self, **kwargs):
        query_filter = {
            self.query_key_field: kwargs[self.query_key_field]
        }
        try:
            obj = self.queryset().get(**query_filter)
            result = self.schema.dump(obj)
            return jsonify(result.data)
        except DoesNotExist:
            return jsonify({'error': 'No object with key \'{}\' found'.format(kwargs[self.query_key_field])}), 404

    def get(self, **kwargs):
        if self.query_key_field not in kwargs or kwargs[self.query_key_field] is None:
            return self.get_list()
        else:
            return self.get_detail(**kwargs)

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No JSON data provided. Make sure to set the content type of your request to: application/json'}), 400
        else:
            parsed_data = self.schema.load(json_data, partial=True)
            if parsed_data.errors:
                return jsonify(parsed_data.errors), 400
            obj = parsed_data.data
            obj.save()
            result = self.schema.dump(obj)
            return jsonify(result.data), 201

    def put(self, **kwargs):
        json_data = request.get_json()
        if kwargs[self.query_key_field] is None:
            return jsonify({'error': 'Parameter \'{}\' must be specified'.format(self.query_key_field)}), 400
        elif not json_data:
            return jsonify({'error': 'No JSON data provided. Make sure to set the content type of your request to: application/json'}), 400
        else:
            query_filter = {
                self.query_key_field: kwargs[self.query_key_field]
            }
            try:
                obj = self.queryset.get(**query_filter)
                obj.modify(**json_data)
                result = self.schema.dump(obj)
                return jsonify(result.data)
            except DoesNotExist:
                return jsonify({'error': 'No object with key \'{}\' found'.format(kwargs[self.query_key_field])}), 404

    def delete(self, **kwargs):
        if kwargs[self.query_key_field] is None:
            return jsonify({'error': 'Parameter \'{}\' must be specified'.format(self.query_key_field)}), 400
        else:
            query_filter = {
                self.query_key_field: kwargs[self.query_key_field]
            }
            try:
                obj = self.queryset.get(**query_filter)
                obj.delete()
                return '', 204
            except DoesNotExist:
                return jsonify({'error': 'No object with key \'{}\' found'.format(kwargs[self.query_key_field])}), 404
