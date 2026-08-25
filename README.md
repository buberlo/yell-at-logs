# Yell At Logs

> Turn messy application logs into passive-aggressive haikus and PR apologies.

A CLI that parses error and warning logs, scores their guilt level, and outputs short poems. It can also post an apologetic comment to a GitHub issue when the logs get embarrassing.

## Features
- Tail or import log files and classify severity with regex rules
- Score each incident on a guilt meter from mild to catastrophic
- Generate haiku or limerick summaries with optional developer guilt levels
- Post generated apologies to GitHub issues or pull requests

## Stack
- Python
- Rich
- Jinja2
- PyGithub

## Getting started
```
pip install -e . && yell-at-logs --file app.log --poem haiku --github-issue 123
```

---
*Farmed 🚜 by [Appshaker](https://github.com/buberlo) — shaken into existence.*
