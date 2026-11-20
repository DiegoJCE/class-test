# Tip Calculator

A small web page that calculates a tip and splits the bill between friends.

## What it does

- Enter a bill amount and pick a tip of 15%, 18% or 20%, or type a custom percent.
- Enter the number of people.
- The page shows the tip, the total, and the per-person amount, and updates as you type.
- Bad input (empty, negative, non-numeric, or zero people) shows a message instead of crashing.

No accounts, no database, no build step.

## How to run

You need Python 3 installed. From the project folder, run:

```
python -m http.server 8000
```

Then open <http://localhost:8000/index.html> in your browser. Press `Ctrl+C` in the terminal to stop the server.

Because the app is plain HTML and JavaScript, you can also just double-click `index.html`.

## Built with

Built by Claude (Opus as planner, Sonnet as builder), with review by Codex.
