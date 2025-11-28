from setuptools import setup, find_packages

setup(
    name="strix",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "google-generativeai",
        "colorama",
        "prompt_toolkit",
    ],
    extras_require={
        "openai": ["openai"],
        "anthropic": ["anthropic"],
        "groq": ["groq"],
        "mistralai": ["mistralai"],
    },
    entry_points={
        "console_scripts": [
            "strix = strix.main:main",
        ],
    },
)
