# File integrity monitor

A python made file integrity monitoring tool that detects changes to files in a
monitored directory using SHA-256 hashing.

This project is a cybersecurity learning project to help me explore and learn
hashing, logging and basic security event handling.

## Features

- Creates a baseline of files using SHA-256 hashes.
- Detects:
	- Added files
	- Deleted files
	- Modified files
- Continuously monitor a directory at a user set interval.
- Ask the user if detected changes were authorized. 
- Logs changes and decisions in `log.json`

## How it works

The program keeps a `baseline.json` file that has the expected state of the 
monitored directory.

Each file is hashed with SHA-256.

When a check happens the program compares the current state of the directory
against the baseline.

When a change is detected it asks if the changed was made by the user.

Baseline is updated only if a changed was an authorized one.

## Usage

### Initialize the baseline

Before monitoring a directory, initialize the baseline:
	`python3 monitor.py --init`

This creates `baseline.json`.

### Check for changes
Run a single integrity check instead of continuous monitoring.
`python3 monitor.py --check`
This only reports detected changes and does not ask the user if changes were authorized.

### Monitor continuously
`python3 monitor.py --monitor`
The program will ask how often a scan for changes should run.
Then the program will scan for changes every set amount of time.
Press CTR+C to stop.

## Limitations

- The program relies on the user to authorize detected changes.
- The monitored directory is hard-coded within the project (Cant set monitored directory).
- Changes are detected by periodic scanning and not filesystem events
- The baseline and log require the right filesystem permissions.

## Why i built this

I built this as a practical introduction to defensive cybersec and python.

I wanted to build a tool that demonstrates real security use cases like detecting unexpected file changes and logging them.

This project helped me practice designing functions, practice dictionaries and lists, handling json data, using hashes, building a CLI, and building a continuously running program.
