# Script Rescue · Malcom Alloc

**A focused fix for a broken Python script or CSV workflow. $125 USD per agreed job.**

A daily export fails. A script turns `00041` into `41`. Duplicate records quietly
double a total. Send a small, sanitized reproduction and the expected output.
We will check whether it fits a fixed-price repair before accepting the work.

## What the $125 scope includes

- One reproducible Python/CSV problem in a small existing workflow.
- Corrected source, a regression check, and clear run instructions.
- A before/after explanation and one correction within the agreed scope.

Scope, acceptance criteria, delivery date, and payment method must be agreed
before a paid job starts. Larger builds, production access, ongoing hosting,
and a new application are outside this offer. No payment is collected here.

**[Request a scope review](https://github.com/malcom-alloc/script-rescue/issues/new?template=repair-request.yml)**

The intake is public: use synthetic samples only. Never post customer records,
credentials, API keys, or private source. If the job needs private material,
describe the problem first and arrange an appropriate private channel.

## See a working example

This is a synthetic demonstration, not a customer project or testimonial.
The example repairs a common failure pattern: an export that mixes usable rows,
duplicate IDs, invalid dates, and malformed amounts.

```sh
python3 demo/clean_export.py demo/input.csv /tmp/script-rescue-example
python3 -m unittest discover -s tests -v
```

Use a new output directory each time. Python 3.10+; no third-party packages.

The nine-row input produces **three accepted records totaling $20.00** and
**six quarantined records** with reasons. `00041` stays `00041`. Both occurrences
of the duplicate ID are quarantined rather than silently choosing a winner.
Dates are explicitly ISO dates and amounts explicitly nonnegative USD values
with at most two decimal places. This is a narrow contract, not a general CSV
cleaner. Currency/locale/date conventions need their own agreed specification.

Browse the [sample input](demo/input.csv), [clean result](demo/expected/clean.csv),
[rejection reasons](demo/expected/rejected.json), and [audit](demo/expected/audit.json).

Output: `clean.csv`, `rejected.json`, and an `audit.json` containing the input
SHA-256 and record counts. Every parsed input record is accounted for; malformed
CSV fails the whole read. Source bytes remain untouched and existing output
directories are refused. Interrupted output writes must be discarded and rerun
to a new directory. Arbitrary input strings are not spreadsheet-formula sanitized;
review the output before opening untrusted fields in spreadsheet software.

## About this service

Malcom Alloc is an AI-assisted software project operated by the account owner.
Implementation and tests use AI assistance. There are no invented credentials,
customer claims, or promises that every problem can be fixed within this scope.
The demonstration source is MIT licensed; paid jobs use separately agreed terms.
