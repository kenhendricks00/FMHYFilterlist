# Contributing

## Adding a website:

Fork the project, add a website in sitelist.txt (or in sitelist-plus.txt if the domain fits in the Plus category) and run build.py then submit a pull request. 

## Adding a redirect alias

Add the original FMHY-listed URL to `redirect-sources.txt`, then run:

```sh
python build_redirects.py
python -m unittest discover -s tests -v
```

Commit both `redirect-sources.txt` and the generated
`filterlist-redirects.json`. The generator follows HTTP redirects, preserves
paths and query strings, removes fragments and unchanged URLs, and fails when
an input URL is invalid or duplicated.
