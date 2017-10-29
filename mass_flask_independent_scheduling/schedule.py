import time
import warnings
from multiprocessing import Pool
from mass_flask_core.models import ScheduledAnalysis, AnalysisRequest
from mass_flask_config.app import app
from mass_flask_independent_scheduling.instance_dictio import InstanceDictio


def _schedule_analysis_request(request):
    system_id = request.analysis_system.id
    instances = InstanceDictio.dictio[system_id]
    min_instance = InstanceDictio.get_instance_with_minimum_count(instances)
    if not InstanceDictio.check_id(system_id):
        return False

    s = ScheduledAnalysis(analysis_system_instance=min_instance, sample=request.sample)
    s.save()
    min_instance.analyses_count += 1

    InstanceDictio.remove_if_threshold_reached(min_instance, system_id)
    request.delete()
    return True
    

def schedule_analyses():
    print("Scheduling...")
    with app.app_context():
        InstanceDictio.update_instance_dict()
        analysis_requests = AnalysisRequest.objects().no_dereference()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with Pool() as p:
                scheduled_list = p.map(_schedule_analysis_request, analysis_requests)
        requests_scheduled = sum(scheduled_list)
        request_not_scheduled = len(scheduled_list) - requests_scheduled
        print('Scheduled: ', requests_scheduled, 'Not scheduled: ', request_not_scheduled)


if __name__ == '__main__':
    while 1:
        schedule_analyses()
        time.sleep(app.config['SCHEDULE_ANALYSES_INTERVAL'])
