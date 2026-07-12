# Contributing

## Adding a website:

Fork the project, add a website in sitelist.txt (or in sitelist-plus.txt if the domain fits in the Plus category) and run build.py then submit a pull request. 

## Adding a redirect alias

Run the full-wiki redirect scan:

```sh
python build_redirects.py
python -m unittest discover -s tests -v
```

Commit the generated `filterlist-redirects.json`. The generator scans resource
links from FMHY's single-page export, follows HTTP redirects concurrently,
preserves paths and query strings, and publishes only cross-host aliases. It
writes URLs that could not be checked to the ignored
`filterlist-redirect-errors.json` review file.

Same-site changes and known authentication, invite, short-link and tracking
redirects are excluded from the published alias file.

`redirect-sources.txt` is only for additional FMHY-listed URLs that are not
discoverable in the wiki export.
