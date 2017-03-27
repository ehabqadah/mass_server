from mongoengine import signals

from mass_server.core.models import Report
from .copy_report_tags import copy_tags_from_report_to_sample
from .dispatch_request import update_dispatch_request_for_new_sample


def connect_signals():
    signals.post_save.connect(update_dispatch_request_for_new_sample)
    signals.post_save.connect(copy_tags_from_report_to_sample, sender=Report)
