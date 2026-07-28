# Assumptions Policy

Facts and assumptions must never be blended without an explicit classification. Classification is separate from confidence: a well-supported estimate can have high confidence while remaining an estimate.

## Verified Facts

Directly stated, observable, or contractually documented values. Store the source-document IDs, effective date, and the exact entity to which the fact applies. SEC filings are confidence level 5; company-confirmed disclosures are level 4.

## Estimated Values

Values inferred where no authoritative figure is available. Record the estimation method, input record IDs, range or sensitivity when appropriate, estimator, and as-of date. Estimates must not overwrite verified facts and must be replaceable when better evidence appears.

## Derived Values

Deterministic results calculated from verified facts and/or explicit estimates. Every derived value must be reproducible: identify input record IDs, transformation name and version, formula or code location, units, and calculation timestamp. Generated outputs are disposable and must not become the sole copy of an underlying fact.

## Confidence levels

| Level | Evidence standard |
| --- | --- |
| 5 | Verified SEC filing |
| 4 | Company confirmed |
| 3 | Multiple independent sources |
| 2 | Credible reporting |
| 1 | Unverified or speculative |

Use the strongest level actually supported. Multiple articles repeating one original report count as one source. Confidence changes must update `modified_at`, retain source history, and explain the reason in `notes` or the review log.
