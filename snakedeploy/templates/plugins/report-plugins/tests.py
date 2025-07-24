from typing import Optional
import snakemake.common.tests
from snakemake_interface_report_plugins.settings import ReportSettingsBase


# Check out the base classes found here for all possible options and methods:
# https://github.com/snakemake/snakemake/blob/main/src/snakemake/common/tests/__init__.py
class TestWorkflowsBase(snakemake.common.tests.TestReportBase):
    __test__ = True

    def get_reporter(self) -> str:
        return "{{plugin_name}}"

    def get_report_settings(self) -> Optional[ReportSettingsBase]:
        # instantiate ReportSettings of this plugin as appropriate
        ...
