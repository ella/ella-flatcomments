test_runner = None
old_config = None

def setup():
    global test_runner
    global old_config
    from django.test.simple import DjangoTestSuiteRunner
    from ella.utils.installedapps import call_modules
    test_runner = DjangoTestSuiteRunner()
    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()
    call_modules(('register', ))

def teardown():
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()


