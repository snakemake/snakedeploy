from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence, Union

from snakemake_interface_scheduler_plugins.settings import SchedulerSettingsBase
from snakemake_interface_scheduler_plugins.base import SchedulerBase
from snakemake_interface_scheduler_plugins.interfaces.jobs import JobSchedulerInterface
from snakemake_interface_common.io import AnnotatedStringInterface


# Optional:
# Define settings for your scheduler plugin.
# They will occur in the Snakemake CLI as --scheduler-<plugin-name>-<param-name>
# Make sure that all defined fields are 'Optional' and specify a default value
# of None or anything else that makes sense in your case.
@dataclass
class SchedulerSettings(SchedulerSettingsBase):
    myparam: Optional[int] = field(
        default=None,
        metadata={
            "help": "Some help text",
            # Optionally request that setting is also available for specification
            # via an environment variable. The variable will be named automatically as
            # SNAKEMAKE_<storage-plugin-name>_<param-name>, all upper case.
            # This mechanism should only be used for passwords, usernames, and other
            # credentials.
            # For other items, we rather recommend to let people use a profile
            # for setting defaults
            # (https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles).
            "env_var": False,
            # Optionally specify a function that parses the value given by the user.
            # This is useful to create complex types from the user input.
            "parse_func": ...,
            # If a parse_func is specified, you also have to specify an unparse_func
            # that converts the parsed value back to a string.
            "unparse_func": ...,
            # Optionally specify that setting is required when the executor is in use.
            "required": True,
            # Optionally specify multiple args with "nargs": True
        },
    )


# Inside of the Scheduler, you can use self.logger (a normal Python logger of type
# logging.Logger) to log any additional informations or warnings.
class Scheduler(SchedulerBase):
    def __post_init__(self) -> None:
        # Optional, remove method if not needed.
        # Perform any actions that shall happen after initialization.
        # Do not overwrite the actual __init__ method, in order to ensure compatibility
        # with future interface versions.
        ...

    def dag_updated(self) -> None:
        # This method is called when the DAG is updated.
        # Use self.dag.needrun_jobs() to get an iterable of all jobs that need to be executed.
        # Use self.dag.dependencies(job) to get an iterable of all dependencies of a job.
        ...

    def select_jobs(
        self,
        selectable_jobs: Sequence[JobSchedulerInterface],
        remaining_jobs: Sequence[JobSchedulerInterface],
        available_resources: Mapping[str, Union[int, str]],
        input_sizes: Mapping[AnnotatedStringInterface, int],
    ) -> Optional[Sequence[JobSchedulerInterface]]:
        # Select jobs from the selectable jobs sequence. Thereby, ensure that the selected
        # jobs do not exceed the available resources.

        # Job resources are available via Job.scheduler_resources.

        # Jobs are either single (SingleJobSchedulerInterface) or group jobs (GroupJobSchedulerInterface).
        # Single jobs inside a group job can be obtained with GroupJobSchedulerInterface.jobs().

        # While selecting, jobs can be given additional resources that are not
        # yet defined in the job itself via Job.add_resource(name: str, value: int | str).

        # The argument remaining_jobs contains all jobs that still have to be executed
        # at some point, including the currently selectable jobs.

        # input_sizes provides a mapping of given input files to their sizes.
        # This can e.g. be used to prioritize jobs with larger input files or to weight
        # the footprint of temporary files. The function uses async I/O under the hood,
        # thus make sure to call it only once per job selection and collect all files of
        # interest for a that single call.

        # Return None to indicate an error in the selection process that shall lead to
        # a fallback to the Snakemake's internal greedy scheduler.
        # Otherwise, return the sequence of selected jobs.
        ...
