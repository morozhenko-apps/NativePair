"""Table-driven unittest registration with a canonical negative category."""

def add_cases(test_class, category, rule, cases, assertion):
    """Register each independent table row as an isolated, countable test."""
    for name, value in cases:
        def test(self, value=value):
            assertion(self, value)
        test.__name__ = f"test_given_{name}_when_{rule}_then_contract_holds"
        test.category = category
        if hasattr(test_class, test.__name__):
            raise ValueError(f"Duplicate scenario: {test.__name__}")
        setattr(test_class, test.__name__, test)


def category(name):
    def decorate(function):
        function.category = name
        return function
    return decorate
