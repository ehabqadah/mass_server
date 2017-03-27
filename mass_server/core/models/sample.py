from flask_modular_auth import current_authenticated_entity
from flask_mongoengine import BaseQuerySet
from mongoengine import StringField, DateTimeField, ListField, ReferenceField, EmbeddedDocumentField, FileField, IntField, FloatField, EmbeddedDocument, LongField, ValidationError, \
    DoesNotExist, Q, GenericReferenceField

from mass_server.core.utils import TimeFunctions, HashFunctions, FileFunctions, ListFunctions, StringFunctions
from mass_server.config.app import db
from .analysis_system import AnalysisSystem
from .comment import CommentsMixin
from .tlp_level import TLPLevelField


class SampleQuerySet(BaseQuerySet):
    def get_with_tlp_level_filter(self):
        if current_authenticated_entity.is_authenticated:
            return self.filter(Q(tlp_level__lte=current_authenticated_entity.max_tlp_level) | Q(created_by=current_authenticated_entity._get_current_object()))
        else:
            return self.filter(tlp_level__lte=current_authenticated_entity.max_tlp_level)


class Sample(db.Document, CommentsMixin):
    delivery_date = DateTimeField(default=TimeFunctions.get_timestamp, required=True)
    first_seen = DateTimeField(default=TimeFunctions.get_timestamp, required=True)
    tags = ListField(StringField(regex=r'^[\w:\-\_\/\+]+$'))
    dispatched_to = ListField(ReferenceField(AnalysisSystem))
    created_by = GenericReferenceField()
    tlp_level = TLPLevelField(verbose_name='TLP Level', help_text='Privacy level of this sample', required=True)

    meta = {
        'allow_inheritance': True,
        'ordering': ['-delivery_date'],
        'indexes': ['delivery_date'],
        'queryset_class': SampleQuerySet
    }

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.id))

    def __str__(self):
        return self.__repr__()

    @property
    def title(self):
        return self.id

    def add_tags(self, tags):
        self.tags = ListFunctions.merge_lists_without_duplicates(self.tags, tags)
        self.save()

    def _update(self, **kwargs):
        if 'first_seen' in kwargs and kwargs['first_seen'] < self.first_seen:
            self.first_seen = kwargs['first_seen']
        if 'tlp_level' in kwargs and not self.tlp_level:
            self.tlp_level = kwargs['tlp_level']
        if current_authenticated_entity.is_authenticated and not self.created_by:
            self.created_by = current_authenticated_entity._get_current_object()
        if 'tags' in kwargs:
            tags = kwargs['tags']
        else:
            tags = []
        self.tags = ListFunctions.merge_lists_without_duplicates(self.tags, tags)

    @classmethod
    def create_or_update(cls, **kwargs):
        raise ValidationError('Samples of the base type Sample should not be instantiated directly.')


class FileSample(Sample):
    file = FileField()
    file_names = ListField(StringField())
    file_size = IntField(required=True)
    magic_string = StringField(required=True)
    mime_type = StringField(required=True)
    md5sum = StringField(max_length=32, required=True)
    sha1sum = StringField(max_length=40, required=True)
    sha256sum = StringField(max_length=64, required=True)
    sha512sum = StringField(max_length=128, required=True)
    ssdeep_hash = StringField(max_length=200, required=True)
    shannon_entropy = FloatField(min_value=0, max_value=8, required=True)

    meta = {
        'allow_inheritance': True,
        'indexes': [{
            'fields': ['md5sum', 'sha1sum', 'sha256sum', 'sha512sum', 'ssdeep_hash', 'shannon_entropy'],
            'unique': False
        }]
    }

    @property
    def title(self):
        return self.file.name

    def _initialize(self, **kwargs):
            file = kwargs['file']
            self.md5sum = HashFunctions.md5_hash(file)
            self.sha1sum = HashFunctions.sha1_hash(file)
            self.sha256sum = HashFunctions.sha256_hash(file)
            self.sha512sum = HashFunctions.sha512_hash(file)
            self.ssdeep_hash = HashFunctions.ssdeep_hash(file)
            self.shannon_entropy = HashFunctions.shannon_entropy(file)
            self.file_size = FileFunctions.get_file_size(file)

            file_name = FileFunctions.get_file_name(file)
            self.mime_type = FileFunctions.get_mime_type_from_file(file)
            self.magic_string = FileFunctions.get_magic_string_from_file(file)
            file_extension = FileFunctions.get_file_extension(file_name)
            self.tags = FileFunctions.assemble_tag_list(self.magic_string, self.mime_type, file_extension)
            self.tags.append('sample-type:filesample')

            self.file.put(file, filename=file_name, content_type=self.mime_type)
            self.add_file_name_to_list(file_name)

    def add_file_name_to_list(self, file_name):
        if file_name not in self.file_names:
            self.file_names.append(file_name)

    @classmethod
    def create_or_update(cls, **kwargs):
        if 'file' not in kwargs:
            raise ValidationError('Parameter file is missing')
        else:
            file = kwargs['file']
            hash_values = HashFunctions.get_hash_values_dictionary(file)
            try:
                sample = cls.objects.get(**hash_values)
            except DoesNotExist:
                if FileFunctions.get_file_type(file) == 'windows-binary':
                    sample = ExecutableBinarySample()
                else:
                    sample = FileSample()
                sample._initialize(**kwargs)
            sample._update(**kwargs)
            sample.save()
            return sample


class FilesystemEvent(EmbeddedDocument):
    FILESYSTEM_EVENT_TYPES = (
        ('c', 'Create'),
        ('d', 'Delete'),
        ('o', 'Open'),
        ('r', 'Read'),
        ('w', 'Write'),
        ('u', 'Unknown')
    )

    file_path = StringField(required=True)
    event_type = StringField(max_length=1, choices=FILESYSTEM_EVENT_TYPES)

    def __hash__(self):
        return hash((self.file_path, self.event_type))


class Section(EmbeddedDocument):
    name = StringField(required=True)
    virtual_address = LongField(min_value=0)
    virtual_size = LongField(min_value=0)
    raw_data_size = LongField(min_value=0)
    shannon_entropy = FloatField(min_value=0, max_value=8)

    def __hash__(self):
        return hash((self.name, self.virtual_address, self.virtual_size, self.raw_data_size, self.shannon_entropy))


class Resource(EmbeddedDocument):
    name = StringField(required=True)
    offset = LongField(min_value=0)
    size = LongField(min_value=0)
    language = StringField()
    sublanguage = StringField()

    def __hash__(self):
        return hash((self.name, self.offset, self.size, self.language, self.sublanguage))


class Import(EmbeddedDocument):
    library_name = StringField()
    import_name = StringField()
    virtual_address = LongField(min_value=0)

    def __hash__(self):
        return hash((self.library_name, self.import_name, self.virtual_address))


class RegistryEvent(EmbeddedDocument):
    REGISTRY_EVENT_TYPES = (
        ('c', 'Create'),
        ('d', 'Delete'),
        ('r', 'Read'),
        ('w', 'Write'),
        ('u', 'Unknown')
    )

    registry_key = StringField(required=True)
    value = StringField()
    event_type = StringField(max_length=1, choices=REGISTRY_EVENT_TYPES)

    def __hash__(self):
        return hash((self.registry_key, self.value, self.event_type))


class ExecutableBinarySample(FileSample):
    filesystem_events = ListField(EmbeddedDocumentField(FilesystemEvent))
    registry_events = ListField(EmbeddedDocumentField(RegistryEvent))
    sections = ListField(EmbeddedDocumentField(Section))
    resources = ListField(EmbeddedDocumentField(Resource))
    imports = ListField(EmbeddedDocumentField(Import))
    strings = ListField(StringField())

    def _initialize(self, **kwargs):
        super(ExecutableBinarySample, self)._initialize(**kwargs)
        self.tags.append('sample-type:executablebinarysample')
        file = kwargs['file']
        # file_path = FileFunctions.get_file_path(file)
        # pe = pefile.PE(data=file.stream)
        # self._get_sections(pe)
        # self._get_imports(pe)

    def _get_sections(self, pe):
        for section in pe.sections:
            s = Section(name=StringFunctions.strip_zero_bytes_from_string(section.Name), virtual_address=section.VirtualAddress, virtual_size=section.Misc_VirtualSize,
                        raw_data_size=section.SizeOfRawData, shannon_entropy=section.get_entropy())
            self.sections.append(s)

    def _get_imports(self, pe):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                i = Import(library_name=entry.dll, import_name=imp.name, virtual_address=imp.address)
                self.imports.append(i)


class IPSample(Sample):
    ip_address = StringField(required=True)

    @property
    def title(self):
        return self.ip_address

    def _initialize(self, **kwargs):
        self.ip_address = kwargs['ip_address']
        self.tags.append('sample-type:ipsample')

    @classmethod
    def create_or_update(cls, **kwargs):
        if 'ip_address' not in kwargs:
            raise ValidationError('Parameter ip_address is missing')
        else:
            try:
                sample = cls.objects.get(ip_address=kwargs['ip_address'])
            except DoesNotExist:
                sample = IPSample()
                sample._initialize(**kwargs)

            sample._update(**kwargs)
            sample.save()
            return sample


class DomainSample(Sample):
    domain = StringField(required=True)

    @property
    def title(self):
        return self.domain

    def _initialize(self, **kwargs):
        self.domain = kwargs['domain']
        self.tags.append('sample-type:domainsample')

    @classmethod
    def create_or_update(cls, **kwargs):
        if 'domain' not in kwargs:
            raise ValidationError('Parameter domain is missing')
        else:
            try:
                sample = cls.objects.get(domain=kwargs['domain'])
            except DoesNotExist:
                sample = DomainSample()
                sample._initialize(**kwargs)

            sample._update(**kwargs)
            sample.save()
            return sample


class URISample(Sample):
    uri = StringField(required=True)

    @property
    def title(self):
        return self.uri

    def _initialize(self, **kwargs):
        self.uri = kwargs['uri']
        self.tags.append('sample-type:urisample')

    @classmethod
    def create_or_update(cls, **kwargs):
        if 'uri' not in kwargs:
            raise ValidationError('Parameter uri is missing')
        else:
            try:
                sample = cls.objects.get(uri=kwargs['uri'])
            except DoesNotExist:
                sample = URISample()
                sample._initialize(**kwargs)

            sample._update(**kwargs)
            sample.save()
            return sample
