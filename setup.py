from setuptools import setup

setup(name='shiningspectrum',
      version='1.0.beta',
      description='A Python package for spectral recognition.',
      url='https://github.com/JunLin615/Shining-Spectrum',
      author='JunLin615,BJUT  in China',
      license='MIT',
      packages=['shiningspectrum'],
      install_requires=['numpy', 'rampy', 'peakutils', 'pywt', 'os', 'pickle', 're', 'scipy', 'math', 'ramannoodles', 'lmfit', 'multiprocessing', 'time'])
