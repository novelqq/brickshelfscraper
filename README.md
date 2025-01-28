# brickshelfscraper
python script that downloads all the relevant images on brickshelf galleries

## Dependencies
Requires Python >=3.9.

```
python -m pip install -r requirements.txt
```

## Instructions
Place each brickshelf gallery URL on a new line in links.txt
Run `python main.py` 
The script will scan all subdirectories and download all the files in a folder called gallery and create sub-directories as necessary. It preserves the folder structure on the website. It also creates .txt files for folder descriptions.
