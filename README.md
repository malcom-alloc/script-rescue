# Script Rescue · Malcom Alloc

A tested, synthetic Python CSV repair demonstration. This repository is a portfolio sample.

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

## License

The demonstration source is MIT licensed.
