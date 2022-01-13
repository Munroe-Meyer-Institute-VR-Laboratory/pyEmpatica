from setuptools import setup, find_packages

setup(name='pyEmpatica',
      version='0.5.6',
      url='https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyEmpatica',
      author='Walker Arce',
      author_email='walker.arce@unmc.edu',
      description='Communicate with your Empatica E4 in your Python scripts.',
      packages=find_packages(),
      long_description=open('README.md').read(),
      zip_safe=False)

# python setup.py bdist_wheel
# pip3 install pdoc3
# pdoc --html --output-dir docs pyempatica
