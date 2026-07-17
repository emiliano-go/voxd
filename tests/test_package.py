"""Verify the heard package tree imports cleanly."""


class TestPackage:
    def test_import_heard(self):
        import heard
        assert heard.__file__ is not None

    def test_all_public_modules_import(self):
        import heard.cli
        import heard.intent
        import heard.stt
        import heard.shell_allowlist
        import heard.tools
        import heard.tools.types
        import heard.tools.registry
        import heard.tools.system_query
        import heard.tools.volume
        import heard.tools.media
        import heard.tools.apps
        import heard.tools.window
        import heard.tools.workspace
        import heard.tools.helpers
        import heard.tools.helpers.network
        import heard.tools.helpers.system
        import heard.tools.helpers.apps

    def test_tools_init(self):
        import heard.tools
        assert heard.tools.__file__ is not None
