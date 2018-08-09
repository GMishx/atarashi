# Atarashi
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

#### To install dependencies only
- `# pip install -r requirements.txt`


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
```sh
# apt-get install python3-setuptools python3-all debhelper python-pip
```
- Get the source distribution file using
```sh
$ python3 setup.py sdist
```
- Copy the archive and rename it
```sh
$ cp dist/atarashi-0.0.9.tar.gz ../atarashi_0.0.9.orig.tar.gz
```
- Build the package
```sh
$ debuild
```
