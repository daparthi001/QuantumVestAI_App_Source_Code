from setuptools import setup, find_packages

setup(
    name="quantumvestai",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Dependencies are already specified in requirements.txt
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="QuantumVestAI financial analytics and investment platform",
    keywords="finance, investments, machine learning, sentiment analysis",
    url="https://github.com/yourusername/quantumvestai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
