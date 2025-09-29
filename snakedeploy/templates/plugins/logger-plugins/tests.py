from snakemake_interface_logger_plugins.tests import TestLogHandlerBase


class TestConcreteRichPlugin(TestLogHandlerBase):
    """Concrete test using the actual rich plugin to verify the abstract test class works."""

    __test__ = True

    def get_log_handler_cls(self):
        """Return the rich log handler class."""
        ...

    def get_log_handler_settings(self):
        """Return the rich settings with default values for testing."""
        ...
