# Ghost Recon Passive Enumerator

A minimal Python application that uses [CrewAI](https://github.com/joaomdmoura/crewai) and the OWASP Amass CLI to perform **passive** subdomain enumeration against a single target domain. One agent runs two sequential tasks: collecting the target domain and performing enumeration using only passive sources.

## Features
- One CrewAI agent with passive Amass tool
- Interactive domain intake (if not provided via CLI)
- Writes parsed subdomains to `outputs/<domain>_subdomains.json`

## Installation
1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install [OWASP Amass](https://github.com/owasp-amass/amass) and ensure the `amass` binary is on your `PATH`.

## Configuration
Set up environment variables (optional) in a `.env` file or your shell:
```bash
export OPENAI_API_KEY=your_key
export MODEL_NAME=gpt-4o-mini  # optional, defaults to gpt-4o-mint
export AUTHORIZED=true         # or use --authorized flag
```

## Usage
```bash
python app.py --domain example.com --authorized
```
If `--domain` is omitted, the program prompts for one interactively.

The result is saved to `outputs/<domain>_subdomains.json` as a JSON array of strings.

## Legal Notice
This tool performs **passive** reconnaissance only. Use it solely on targets for which you have explicit permission. The authors and contributors are not responsible for misuse.
