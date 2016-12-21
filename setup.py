from setuptools import setup, find_packages


setup(
    name="kapp",
    version="1.0.0",
    description="Keep alive python proxy",
    author="Subir Jolly",
    author_email="subirjolly@gmail.com",
    license="Open Source License.",
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        "console_scripts": ["kapp=scripts.run:main"]
    }
)

