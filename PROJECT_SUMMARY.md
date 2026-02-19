# PlayBook — Project Summary (Shareable)

**Last updated:** February 2026  
**Purpose:** Exportable summary of what’s been built so far for sharing with your group.

---

## What PlayBook Is

PlayBook is a **group trip planning app** for Scottsdale-area trips (Spring Training, Bachelorette, WM Phoenix Open). One organizer sets up the trip; the group votes on preferences; the app reconciles preferences and generates two itinerary options (Plan A premium, Plan B balanced). The organizer selects a plan, confirms or swaps venues, pays to lock, and exports the final itinerary.

---

## Features Implemented

### Planning mode and flow
- **Solo vs Group choice first** — User picks “Solo Trip Planner” or “Group Trip Planner”; only the relevant flow is shown.
- **Solo path** — Theme, vibes, dates, budget → Generate Itinerary → single plan → confirm/swap → pay → export.
- **Group path** — Theme, vibes, dates, group size, budget → Create Trip for Group → share link → collect votes → Generate Plan A & B → select plan → confirm/swap → pay → view confirmed trip and export.

### Trip creation and sharing (group)
- Organizer creates trip with theme, dates, group size, budget, trip name.
- **Share link** generated (e.g. `http://localhost:8502/?trip=abc123`); shareable via copy button (clipboard icon).
- Optional **email-invite flow** (demo: enter emails; in production would send voting link).
- **Organizer’s choices count as the first vote** so they don’t vote again.
- When a trip is active, the welcome page shows only: trip status, vote count, share link, “View Vote Results,” and “Generate Plan A & B” — no re-entering theme/vibes/dates/budget.

### Group voting
- Group members open the share link (no account required).
- **Vote page:** pick up to 3 vibes (party, relax, foodie, active, sports, luxury, spa, shopping, casino, etc.).
- **Optional free-text** for preferences (e.g. “must have pool day”); used as must-haves in itinerary generation.
- Vote confirmation shown after submit.
- **Vote Results** page shows counts and “Generate Plan A & B” when organizer is ready.

### AI preference reconciliation
- Votes are aggregated and weighted (by group size).
- **Reconciled preference profile** is computed (e.g. party 0.7, foodie 0.5) and used to drive venue selection.
- No separate “conflict resolution” UI — reconciliation is algorithmic; results appear in the two plans.

### Plan A & Plan B
- **Plan A (Premium):** higher price tier, more luxury-oriented venues.
- **Plan B (Balanced):** mid-range, balanced value.
- **Comparison** shown: labels, average tier, key differences.
- Organizer selects Plan A or Plan B; selected plan becomes the active itinerary for confirm/swap and export.

### Itinerary and confirm flow
- **Itinerary page:** day-by-day slots with venue, time, type; optional **travel times** between venues (distance-based).
- **Swap:** pick alternatives from recommendations; **Confirm** or **Skip** per slot.
- **Confirm Plan** section: pay to lock (Stripe link or “I have Paid” demo). After payment, user is sent to the **Confirmed Trip** page (no export options left on the itinerary page).

### Confirmed Trip (final page)
- **Header:** “Trip locked” and short subhead.
- **Theme & vibes** — e.g. “Spring Training • Party, Sports, Active” (and “based on group preferences” for group trips).
- **Trip summary** — enthusiastic write-up (AI-generated) plus day descriptions where available.
- **Full itinerary** — read-only, by day, with times and venues.
- **Export:** Download iCal (.ics), Download HTML (print to PDF), Save as PDF (open HTML then Print → Save as PDF).
- **Back to itinerary** button to return to edit view if needed.

### UX and polish
- **Share link:** copy button (clipboard icon) next to the link; link text is white on dark backgrounds for readability; trip status bar link is dark blue, larger text.
- **Cluster recommendations** — e.g. “Recommended for you: Spring Training + Old Town” from theme + vibes + venue areas.
- **Must-haves from free text** — e.g. “must have pool day” or “nice dinner” reflected in generated itineraries.
- **Readability** — darker step instructions, clearer labels, radio styling; Create Group Trip block at bottom of welcome form.
- **Duplicate-widget and indentation fixes** applied where needed.

### Technical
- **Trip storage:** file-based MVP — `trips/{trip_id}.json` (trip params, votes, reconciled preferences).
- **Venues:** `venues.json` with optional `lat`/`lon` and `area` for travel times and cluster logic.
- **Stack:** Streamlit app; Stripe payment link (optional); no real booking APIs yet (Phase 1 = coordination + deep links/mock codes).

---

## How This Matches the Phase 1 Proposal

- **One organizer + link-based group voting** — Implemented.
- **Preference reconciliation (AI step-change)** — Implemented; votes → reconciled profile → Plan A/B.
- **Plan A/B generation and comparison** — Implemented.
- **Decision convergence** — Organizer selects plan; swap/confirm then lock and export.
- **Lock & export** — Pay to lock → Confirmed Trip page → export iCal, HTML, PDF.
- **Out of scope for Phase 1 (unchanged):** real-time multi-user editing, actual booking APIs, accounts, complex conflict UI.

---

## How to Share This With Your Group

- **Option 1:** Share the file `PROJECT_SUMMARY.md` from the repo (e.g. email, Slack, or export to PDF via your editor or a Markdown-to-PDF tool).
- **Option 2:** Copy the contents into a Google Doc or Notion and adjust formatting if needed.
- **Option 3:** Use “Export” in your editor (e.g. “Markdown: Export to PDF” or “Export to HTML”) and send the exported file.

If you want a shorter “one-pager” or a slide-style version, that can be added as a separate section or file.
