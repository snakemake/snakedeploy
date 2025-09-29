from snakedeploy.exceptions import UserError
from snakedeploy.scaffold_plugins.executor_plugins import (
    ScaffoldSnakemakeExecutorPlugin,
)
from snakedeploy.scaffold_plugins.report_plugins import ScaffoldSnakemakeReportPlugin
from snakedeploy.scaffold_plugins.scheduler_plugins import (
    ScaffoldSnakemakeSchedulerPlugin,
)
from snakedeploy.scaffold_plugins.software_deployment_plugins import (
    ScaffoldSnakemakeSoftwareDeploymentPlugin,
)
from snakedeploy.scaffold_plugins.storage_plugins import ScaffoldSnakemakeStoragePlugin
from snakedeploy.scaffold_plugins.logger_plugins import ScaffoldSnakemakeLoggerPlugin


def scaffold_plugin(plugin_type: str):
    match plugin_type:
        case "software-deployment":
            scaffold = ScaffoldSnakemakeSoftwareDeploymentPlugin()
        case "executor":
            scaffold = ScaffoldSnakemakeExecutorPlugin()
        case "report":
            scaffold = ScaffoldSnakemakeReportPlugin()
        case "storage":
            scaffold = ScaffoldSnakemakeStoragePlugin()
        case "scheduler":
            scaffold = ScaffoldSnakemakeSchedulerPlugin()
        case "logger":
            scaffold = ScaffoldSnakemakeLoggerPlugin()
        case _:
            raise UserError(f"Unknown plugin type: {plugin_type}")
    scaffold.handle()
