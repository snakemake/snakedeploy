from typing import Optional, Type
from snakemake_interface_scheduler_plugins.base import SchedulerBase
from snakemake_interface_scheduler_plugins.settings import SchedulerSettingsBase
from snakemake_interface_scheduler_plugins.tests import TestSchedulerBase


class TestGreedyScheduler(TestSchedulerBase):
    # This ensures that the tests from the base class are executed.
    # Set to False if you want to implement intermediate base classes.
    __test__ = True

    def get_scheduler_cls(self) -> Type[SchedulerBase]:
        # Return the scheduler class of your plugin.
        ...

    def get_scheduler_settings(self) -> Optional[SchedulerSettingsBase]:
        # Return the SchedulerSettings instance you want to test.
        # Note that you can put here multiple classes inheriting from TestSchedulerBase
        # or from each other to test different settings.
        ...
