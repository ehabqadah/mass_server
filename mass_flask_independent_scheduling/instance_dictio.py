import sys
from flask import current_app
from mass_flask_core.models import AnalysisSystemInstance, ScheduledAnalysis


class InstanceDictio:
    dictio = {}

    @staticmethod
    def instance_dict():
        return InstanceDictio.dictio

    @staticmethod
    def update_instance_dict():
        instances = AnalysisSystemInstance.objects().no_dereference()
        for instance in instances:
            if instance.analysis_system.id not in InstanceDictio.dictio.keys():
                InstanceDictio.dictio[instance.analysis_system.id] = list()
            if not instance.is_online:
                continue
            instance.analyses_count = ScheduledAnalysis.objects(analysis_system_instance=instance).count()
            if instance.analyses_count <= current_app.config['MAX_SCHEDULE_THRESHOLD']:
                InstanceDictio.dictio[instance.analysis_system.id].append(instance)

    @staticmethod
    def get_instance_with_minimum_count(instance_list):
        min_count = sys.maxsize
        min_instance = None
        for instance in instance_list:
            if instance.analyses_count < min_count:
                min_count = instance.analyses_count
                min_instance = instance
        return min_instance

    @staticmethod
    def check_id(ident):
        if ident not in InstanceDictio.dictio:
            return False
        if len(InstanceDictio.dictio[ident]) == 0:
            return False
        return True

    @staticmethod
    def remove_if_threshold_reached(instance, system_id):
        if instance.analyses_count > current_app.config['MAX_SCHEDULE_THRESHOLD']:
            InstanceDictio.dictio[system_id].remove(instance)
