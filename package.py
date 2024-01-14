name = "test_package1"

version = "0.2.0"

authors = ["doesn't matter"]

description = "For testing purposes."

uuid = "03d67086ffe54f669b16e72a975ddb8d"

requires = ["python-3+"]

private_build_requires = [
    "python-3+",
    "rezbuild_utils",
]

build_command = "python {root}/build.py"

doc_publish_command = "python {root}/doc/publish-doc.py"

doc_publish_requires = [
    "python-3+",
    "sphinx",
    "furo",
]

cachable = False

tools = []


def commands():
    env.PYTHONPATH.append("{root}/python")
