from snakemake_interface_logger_plugins.base import LogHandlerBase
from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogHandlerSettings(LogHandlerSettingsBase):
    myparam: Optional[int] = field(
        default=None,
        metadata={
            "help": "Some help text",
            # Optionally request that setting is also available for specification
            # via an environment variable. The variable will be named automatically as
            # SNAKEMAKE_LOGGER_<LOGGER-name>_<param-name>, all upper case.
            # This mechanism should ONLY be used for passwords and usernames.
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
            # Optionally specify that setting is required when the LOGGER is in use.
            "required": True,
            # Optionally specify multiple args with "nargs": "+"
        },
    )


class LogHandler(LogHandlerBase):
    def __post_init__(self) -> None:
        # initialize additional attributes
        # Do not overwrite the __init__ method as this is kept in control of the base
        # class in order to simplify the update process.
        # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/main/src/snakemake_interface_logger_plugins/base.py # noqa: E501
        # for attributes of the base class.
        # In particular, the settings of above LogHandlerSettings class are accessible via
        # self.settings.
        # You also have access to self.common_settings here, which are logging settings supplied by the caller in the form of OutputSettingsLoggerInterface. # noqa: E501
        # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/main/src/snakemake_interface_logger_plugins/settings.py for more details # noqa: E501
        ...

    # Here you can override logging.Handler methods to customize logging behavior.
    # For example, you can override the emit() method to control how log records
    # are processed and output. See the Python logging documentation for details:
    # https://docs.python.org/3/library/logging.html#handler-objects

    # LogRecords from Snakemake carry contextual information in the record's attributes
    # Of particular interest is the 'event' attribute, which indicates the type of log information contained
    # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/2ab84cb31f0b92cf0b7ee3026e15d1209729d197/src/snakemake_interface_logger_plugins/common.py#L33 # noqa: E501
    # For examples on parsing LogRecords, see https://github.com/cademirch/snakemake-logger-plugin-snkmt/blob/main/src/snakemake_logger_plugin_snkmt/parsers.py # noqa: E501

    @property
    def writes_to_stream(self) -> bool:
        # Whether this plugin writes to stderr/stdout.
        # If your plugin writes to stderr/stdout, return
        # true so that Snakemake disables its stderr logging.
        ...

    @property
    def writes_to_file(self) -> bool:
        # Whether this plugin writes to a file.
        # If your plugin writes log output to a file, return
        # true so that Snakemake can report your logfile path at workflow end.
        ...

    @property
    def has_filter(self) -> bool:
        # Whether this plugin attaches its own filter.
        # Return true if your plugin provides custom log filtering logic.
        # If false is returned, Snakemake's DefaultFilter will be attached see: https://github.com/snakemake/snakemake/blob/960f6a89eaa31da6014e810dfcf08f635ac03a6e/src/snakemake/logging.py#L372 # noqa: E501
        # See https://docs.python.org/3/library/logging.html#filter-objects for info on how to define and attach a Filter
        ...

    @property
    def has_formatter(self) -> bool:
        # Whether this plugin attaches its own formatter.
        # Return true if your plugin provides custom log formatting logic.
        # If false is returned, Snakemake's Defaultformatter will be attached see: https://github.com/snakemake/snakemake/blob/960f6a89eaa31da6014e810dfcf08f635ac03a6e/src/snakemake/logging.py#L132 # noqa: E501
        # See https://docs.python.org/3/library/logging.html#formatter-objects for info on how to define and attach a Formatter
        ...

    @property
    def needs_rulegraph(self) -> bool:
        # Whether this plugin requires the DAG rulegraph.
        # Return true if your plugin needs access to the workflow's
        # directed acyclic graph for logging purposes.
        ...
