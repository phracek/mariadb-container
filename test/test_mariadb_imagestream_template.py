import os
import sys

import pytest

from container_ci_suite.openshift import OpenShiftAPI
from container_ci_suite.utils import check_variables

if not check_variables():
    print("At least one variable from IMAGE_NAME, OS, VERSION is missing.")
    sys.exit(1)


VERSION = os.getenv("VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
OS = os.getenv("TARGET")
TAGS = {
    "rhel8": "-el8",
    "rhel9": "-el9",
    "rhel10": "-el10"
}
TAG = TAGS.get(OS, None)


class TestMariaDBImagestreamTemplate:

    def setup_method(self):
        self.oc_api = OpenShiftAPI(pod_name_prefix="mariadb", version=VERSION, shared_cluster=True)

    def teardown_method(self):
        self.oc_api.delete_project()

    @pytest.mark.parametrize(
        "template",
        [
            "mariadb-ephemeral-template.json",
            "mariadb-persistent-template.json"
        ]
    )
    def test_mariadb_imagestream_template(self, template):
        if OS == "rhel10":
            pytest.skip("Skipping test for rhel10")
        os_name = ''.join(i for i in OS if not i.isdigit())
        assert self.oc_api.deploy_image_stream_template(
            imagestream_file=f"imagestreams/mariadb-{os_name}.json",
            template_file=f"examples/{template}",
            app_name=self.oc_api.pod_name_prefix
        )
        assert self.oc_api.is_pod_running(pod_name_prefix=self.oc_api.pod_name_prefix)
