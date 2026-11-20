# Marin Software

Marin Software lets County of Marin staff search the County of Marin's SB272 catalog of enterprise software systems by name, vendor or purpose, and filter by custodian department. It reads the County's public [Enterprise Software Systems](https://data.marincounty.gov/resource/ihh2-e4ix) dataset in the browser. Nothing is stored on a server.

## Structure

- `index.html`: the app page
- `assets/app.js`: loads the dataset, keeps a short-lived copy in the browser, and draws the results
- `assets/search-layout.js`: the search and filter behavior (search text, filter groups, the address, the result count)
- `assets/app.css`: the look of the result list
- `vendor/`: the installed MarinOS App Shell
- `security.json`: the security profile; the Content Security Policy in `index.html` is generated from it with `python3 scripts/sync-security-meta.py --write`

This app used to be a tool inside Marin Docs. Its old address there forwards here.

## Run locally

From this folder, run `python3 -m http.server 8765 --bind 127.0.0.1` and open `http://127.0.0.1:8765/`.

## Checks

Run `bash scripts/check.sh`. No browser tests are included yet; `bash scripts/check.sh` runs the shell, security and syntax checks.

## Security

Marin Software follows the [MarinOS security standard](https://github.com/marincountygov/marin-digital-standards/blob/main/security/standard.md). See [`SECURITY.md`](SECURITY.md) to report an issue.
