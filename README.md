# ohsome-examples
Here you find examples and use cases for the ohsome API using jupyter notebooks.

## Jupyter Notebooks
* [Analysing HOT Tasking Manager Projects in Nepal](/python/ohsome_nepal_hot_tm_analysis.ipynb)

## Documentation of Ressources:
* [ohsome Rest-API](http://api.ohsome.org)
* [HOT Tasking Manager API](https://tasks.hotosm.org/api-docs/swagger-ui/index.html?url=https://tasks.hotosm.org/api/docs)

## Installation

Get the git repository.
```bash
git clone 
https://github.com/GIScience/ohsome-examples.git
cd ohsome-examples
```

Set up and activate virtual environment.
```bash
# Linux
python3 -m venv venv
source venv/bin/activate
```
or
```bash
# Windows
python3 -m venv venv
cd venv/Scripts
activate
cd ../..
```


Install all required python-packages.
```
pip install -r requirements.txt
ipython kernel install --user --name=ohsome-examples
```

Run jupyter notebook.
```bash
jupyter notebook
```
