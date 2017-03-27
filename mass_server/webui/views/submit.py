from flask import url_for, render_template, redirect

from mass_server.core.models import FileSample, IPSample, DomainSample, URISample
from mass_server.webui.config import webui_blueprint
from mass_server.webui.forms import FileSampleSubmitForm, IPSampleSubmitForm, DomainSampleSubmitForm, URISampleSubmitForm


@webui_blueprint.route('/submit/file/', methods=['GET', 'POST'])
def submit_file():
    form = FileSampleSubmitForm()
    if form.validate_on_submit():
        sample = FileSample.create_or_update(file=form.data['file'], tlp_level=form.data['tlp_level'])
        return redirect(url_for('webui.sample_detail', sample_id=sample.id))
    return render_template('submit.html', form=form, submit_mode="file")


@webui_blueprint.route('/submit/ip/', methods=['GET', 'POST'])
def submit_ip():
    form = IPSampleSubmitForm()
    if form.validate_on_submit():
        sample = IPSample.create_or_update(ip_address=form.data['ip_address'], tlp_level=form.data['tlp_level'])
        return redirect(url_for('webui.sample_detail', sample_id=sample.id))
    return render_template('submit.html', form=form, submit_mode="ip")


@webui_blueprint.route('/submit/domain/', methods=['GET', 'POST'])
def submit_domain():
    form = DomainSampleSubmitForm()
    if form.validate_on_submit():
        sample = DomainSample.create_or_update(domain=form.data['domain'], tlp_level=form.data['tlp_level'])
        return redirect(url_for('webui.sample_detail', sample_id=sample.id))
    return render_template('submit.html', form=form, submit_mode="domain")


@webui_blueprint.route('/submit/uri/', methods=['GET', 'POST'])
def submit_uri():
    form = URISampleSubmitForm()
    if form.validate_on_submit():
        sample = URISample.create_or_update(uri=form.data['uri'], tlp_level=form.data['tlp_level'])
        return redirect(url_for('webui.sample_detail', sample_id=sample.id))
    return render_template('submit.html', form=form, submit_mode="uri")
