from flask.ext.marshmallow.fields import URLFor
from mass_flask_core.models import SampleRelation
from mass_flask_core.models import DroppedBySampleRelation
from mass_flask_core.models import ResolvedBySampleRelation
from mass_flask_core.models import ContactedBySampleRelation
from mass_flask_core.models import RetrievedBySampleRelation
from mass_flask_core.models import SsdeepSampleRelation
from mass_flask_core.models import Sample
from mass_flask_api.config import api_blueprint
from .base import BaseSchema
from .base import ForeignReferenceField
from marshmallow.fields import Float


class SampleRelationSchema(BaseSchema):
    url = URLFor('.sample_relation', id='<id>', _external=True)
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')

    class Meta(BaseSchema.Meta):
        model = SampleRelation
        dump_only = [
                'id',
                '_cls'
                ]

api_blueprint.apispec.definition('SampleRelation', schema=SampleRelationSchema)


class DroppedBySampleRelationSchema(SampleRelationSchema):
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')

    class Meta(BaseSchema.Meta):
        model = DroppedBySampleRelation
        dump_only = SampleRelationSchema.Meta.dump_only

api_blueprint.apispec.definition('DroppedBySampleRelation', schema=DroppedBySampleRelationSchema)


class ResolvedBySampleRelationSchema(SampleRelationSchema):
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')

    class Meta(BaseSchema.Meta):
        model = ResolvedBySampleRelation
        dump_only = SampleRelationSchema.Meta.dump_only

api_blueprint.apispec.definition('ResolvedBySampleRelation', schema=ResolvedBySampleRelationSchema)


class ContactedBySampleRelationSchema(SampleRelationSchema):
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')

    class Meta(BaseSchema.Meta):
        model = ContactedBySampleRelation
        dump_only = SampleRelationSchema.Meta.dump_only

api_blueprint.apispec.definition('ContactedBySampleRelation', schema=ContactedBySampleRelationSchema)


class RetrievedBySampleRelationSchema(SampleRelationSchema):
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')

    class Meta(BaseSchema.Meta):
        model = RetrievedBySampleRelation
        dump_only = SampleRelationSchema.Meta.dump_only

api_blueprint.apispec.definition('RetrievedBySampleRelation', schema=RetrievedBySampleRelationSchema)


class SsdeepSampleRelationSchema(SampleRelationSchema):
    sample = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    other = ForeignReferenceField(endpoint='mass_flask_api.sample', queryset=Sample.objects(), query_parameter='id')
    match = Float()

    class Meta(BaseSchema.Meta):
        model = SsdeepSampleRelation
        dump_only = SampleRelationSchema.Meta.dump_only

api_blueprint.apispec.definition('SsdeepSampleRelation', schema=SsdeepSampleRelationSchema)
