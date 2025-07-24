from typing import Optional, Type
from snakemake_interface_software_deployment_plugins.tests import (
    TestSoftwareDeploymentBase,
)
from snakemake_interface_software_deployment_plugins import (
    EnvSpecBase,
    EnvBase,
)
from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)


# There can be multiple subclasses of SoftwareDeploymentProviderBase here.
# This way, you can implement multiple test scenarios.
# For each subclass, the test suite tests the environment activation and execution
# within, and, if applicable, environment deployment and archiving.
class TestSoftwareDeployment(TestSoftwareDeploymentBase):
    __test__ = True  # activate automatic testing
    # optional, default is "bash" change if your test suite requires a different
    # shell or you want to have multiple instance of this class testing various shells
    shell_executable = "bash"

    def get_env_spec(self) -> EnvSpecBase:
        # If the software deployment provider does not support deployable environments,
        # this method should return an existing environment spec that can be used
        # for testing
        ...

    def get_env_cls(self) -> Type[EnvBase]:
        # Return the environment class that should be tested.
        ...

    def get_software_deployment_provider_settings(
        self,
    ) -> Optional[SoftwareDeploymentSettingsBase]:
        # If your plugin has settings, return a valid settings object here.
        # Otherwise, return None.
        ...

    def get_test_cmd(self) -> str:
        # Return a test command that should be executed within the environment
        # with exit code 0 (i.e. without error).
        ...
