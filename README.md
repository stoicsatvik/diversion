# diversion

An open, evidence-first project for mapping and evaluating temporary highway traffic management in India.

## Why this exists
Repeated temporary signs, barriers and diversions were observed on a road journey from Mumbai towards Nashik on 10 November 2026. The goal is not to assume these are unsafe or excessive, but to **measure** work-zone signage, visibility, maintenance and navigation clarity, then report verified defects through appropriate channels.

## Research questions
1. Where do work zones start and end, and how are they distributed along the corridor?
2. How many *unique physical signs* appear per kilometre, by type?
3. Which signs are damaged, obscured, redundant, or potentially contradictory?
4. Are advance-warning distances and lane transitions consistent with applicable traffic-management guidance?
5. Can future, independently labelled observations support a model of navigation difficulty?

## Evidence status
Initial observations: five passenger photographs shared in conversation. They show temporary concrete barriers, arrows, "GO SLOW" signs, a 20 km/h sign and a diversion sign. The exact location of each image, road authority, work-zone limits, sign counts, and any actual safety violation remain **unverified**. The source photos have not yet been uploaded to this repository.

## Data
- data/observations.csv: one row per unique physical sign or barrier, not one row per image or arrow.
- physical_object_id is the stable identity across repeated views. Re-observing the same sign in another photo must reuse the same ID; do not create another object row.
- Put multiple evidence references for one object in its evidence_file cell, separated by semicolons. observation_id remains the unique row/record ID.
- data/segments.csv: surveyed road segments including segments with zero signs (essential to avoid selection bias).
- data/initial_observations.md: qualitative notes from the first five images.
- scripts/analyze.py: standard-library CSV analysis; refuses to infer missing measurements and rejects duplicate physical-object IDs.

## Quick start
~~~bash
python3 scripts/analyze.py
~~~
Add observations and segment records with stable IDs and known distances before expecting quantitative output. Blank unknown fields are preferable to fabricated precision.

## Measurement rules
- One physical sign = one physical_object_id, even if it appears in many video frames or photographs.
- Keep one row per physical object and attach all known evidence references to that row.
- Separate distinct work-zone segments; log road direction.
- Record unknown as blank; do not silently treat unknown as zero.
- Mark uncertainty, obstruction, and visibility explicitly.
- Do not infer sign coordinates from the viewer's current location.
- Report damaged signs as observations, not established legal violations.
- Video timestamps and GPS timestamps must be synchronized before geospatial analysis.

## Roadmap
1. Collect location-verified field samples, including control segments.
2. Generate descriptive metrics and an evidence-linked map.
3. Compare findings against relevant IRC/MoRTH traffic management guidance and verified authority plans.
4. Produce a reviewable report and submit verified actionable defects.
5. Only then explore detection/tracking and forecasting, with labelled outcomes and holdout routes.

## Safety and privacy
Only passengers should record while moving; never distract the driver, stop in a live work zone, or enter restricted construction areas. Avoid publishing identifiable faces or number plates. Strip sensitive metadata from public images where appropriate.

## Limitations
This is a citizen-research prototype, not a certified road-safety audit. Sign density alone cannot establish unsafe or inefficient signage. Work-zone complexity, road geometry and traffic volumes matter.
