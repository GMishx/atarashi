# Atarashi
This is a Google Summer of Code Project.  
New License Scanner Project Which Should be Integrated with FOSSology but also Work Independently.

### Requirements
- Python v3.x
- pip

## Steps for Installation
### Build (optional)
- `$ python setup.py build`
- Build will generate 3 new files in your current directory
    1.  `data/Ngram_keywords.json`
    2.  `licenses/<SPDX-version>.csv`
    3.  `licenses/processedList.csv`
- These files will be placed to their appropriate places by the install script.
### Install
- `# python setup.py install`
- In install folder, make the "atarashi-install.sh" executable
- Run <./atarashi-install.sh>
- pip install -r <pathto/requirements.txt>


## How to run
Get the help by running `atarashi -h` or `atarashi --help`
### Example
- Running **DLD** agent

    `atarashi -a DLD /path/to/file.c`
- Running **wordFrequencySimilarity** agent

    `atarashi -a wordFrequencySimilarity /path/to/file.c`
- Running **tfidf** agent
    - With **Cosine similarity**

        `atarashi -a tfidf /path/to/file.c`

        `atarashi -a tfidf -s CosineSim /path/to/file.c`
    - With **Score similarity**

        `atarashi -a tfidf -s ScoreSim /path/to/file.c`
- Running **Ngram** agent
    - With **Cosine similarity**

        `atarashi -a Ngram /path/to/file.c`

        `atarashi -a Ngram -s CosineSim /path/to/file.c`
    - With **Dice similarity**

        `atarashi -a Ngram -s DiceSim /path/to/file.c`
    - With **Bigram Cosine similarity**

        `atarashi -a Ngram -s BigramCosineSim /path/to/file.c`
- Running in **verbose** mode

    `atarashi -a DLD -v /path/to/file.c`
- Running with custom CSVs and JSONs
    - Please reffer to the build instructions to get the CSV and JSON
    understandable by atarashi.
    - `atarashi -a DLD -l /path/to/processedList.csv /path/to/file.c`
    - `atarashi -a Ngram -l /path/to/processedList.csv -j /path/to/ngram.json /path/to/file.c`


### Test
- Run imtihaan (meaning *Exam* in Hindi) with the name of the Agent.
- eg. `python atarashi/imtihaan.py /path/to/processedList.csv <DLD|tfidf|Ngram> <testfile>`
- See `python atarashi/imtihaan.py --help` for more

## Creating Debian packages
- Install dependencies
```
# apt-get install python3-setuptools python3-all debhelper
# pip install stdeb
```
- Create Debian packages
```
$ python3 setup.py --command-packages=stdeb.command bdist_deb
```
- Locate the files under `deb_dist`

## How to generate the documentation using sphinx

1. Go to project directory 'atarashi'
2. export PYTHONPATH=$PYTHONPATH:${PWD}
    - PYTHONPATH sets the search path for the importing python module.
3. Install Sphinx `pip install sphinx` (Since this project is based on python so `pip` is already installed)
4. In the project directory, `sphinx-quickstart`
    - `Root path for the documentation [.]: docs`
    - `Separate source and build directories (y/n) [n]: y`
    - `autodoc: automatically insert docstrings from modules (y/n) [n]: y`
    -  Else use the default option
5. Auto-generate the .rst files in docs/source which will be used to generate documentation 
    - `sphinx-autodoc -o docs/source atarashi/`
6. `cd docs`
7. `make html`

This will generate file in docs/build/html. Go to: index.html

You can change the theme of the documentation by changing the config.py file in docs/source folder. You can choose from {'alabaster', 'classic', 'sphinxdoc', 'scrolls', 'agogo', 'traditional', 'nature', 'haiku', 'pyramid', 'bizstyle'} 
[Reference](http://www.sphinx-doc.org/en/master/theming.html)  


