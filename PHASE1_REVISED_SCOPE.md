# Phase 1 Revised Scope: Focused & Realistic

## Core Insight
**One organizer + group voting** is more realistic and still demonstrates AI value prop (preference reconciliation, conflict resolution).

---

## What to ELIMINATE from Original Phase 1

### ❌ Remove: Full Multi-User Coordination
- **Why**: Too complex for Phase 1 validation
- **Reality**: One organizer managing the trip is standard (bachelorette planner, group trip organizer)
- **Keep**: Group input via voting (simpler, more scalable)

### ❌ Remove: Real-Time Collaboration
- **Why**: Adds complexity without core value
- **Reality**: Group trips don't need real-time editing
- **Keep**: Asynchronous voting/feedback (email link → vote → done)

### ❌ Remove: Complex Conflict Resolution UI
- **Why**: Can be handled algorithmically
- **Reality**: AI reconciles preferences behind the scenes
- **Keep**: Show reconciliation results (e.g., "Group voted for party + foodie, prioritizing party venues")

### ✅ Keep: Preference Reconciliation (Core AI Value)
- **How**: Group votes on vibes → AI weights votes → generates Plan A/B
- **Value**: Shows AI handling the "messy group preferences" problem

### ✅ Keep: Plan A/B Generation
- **How**: Two variants based on reconciled preferences
- **Value**: Demonstrates trade-off analysis and decision convergence

---

## Revised Phase 1 Flow

### Step 1: Organizer Creates Trip
- **Who**: One person (the organizer/planner)
- **Inputs**:
  - Theme (Spring Training, Bachelorette, WMPO)
  - Dates (arrival/departure)
  - Group size
  - Budget range
  - Trip name/description (optional)
- **Output**: Trip created, unique shareable link generated

### Step 2: Group Members Vote on Preferences
- **How**: Organizer shares link via email/SMS
- **What Group Members Do**:
  - Click link → see trip details
  - Vote on vibes (select up to 3 from: party, relax, foodie, active, sports, luxury, spa, shopping, casino)
  - Optional: Add free-text preferences ("must have pool day", "avoid late nights")
  - Submit votes
- **No Account Required**: Link-based voting (low friction)

### Step 3: AI Preference Reconciliation
- **What Happens**:
  - AI aggregates votes (weighted by group size)
  - Identifies conflicts (e.g., "party" vs "relax" votes)
  - Resolves conflicts (prioritize majority, but include minority preferences where possible)
  - Generates preference profile: `{"party": 0.7, "foodie": 0.5, "relax": 0.3}`
- **Output**: Reconciled preference profile ready for itinerary generation

### Step 4: Generate Plan A/B
- **Who**: Organizer (after voting closes or deadline)
- **Input**: Reconciled preferences + organizer's trip parameters
- **Output**: Two itinerary variants:
  - **Plan A**: Premium (higher price_tier, luxury vibes)
  - **Plan B**: Balanced (mid-range, balanced vibes)
- **Show Trade-offs**: Budget difference, venue quality, key differences

### Step 5: Group Decision Convergence
- **How**: Organizer shares Plan A/B with group
- **Options**:
  - Organizer selects (if they have final say)
  - Group votes on Plan A vs Plan B (via same link system)
  - Or: Organizer can still swap/confirm individual slots (current functionality)

### Step 6: Lock & Export
- **Same as current**: Confirm plan → Pay to lock → Export iCal/HTML

---

## What This Achieves (AI Value Prop)

### ✅ Preference Reconciliation (Core AI Step-Change)
- **Problem**: Group has conflicting preferences (party vs relax, luxury vs budget)
- **AI Solution**: Automatically weights votes, resolves conflicts, creates balanced preference profile
- **Value**: Organizer doesn't have to manually reconcile 10+ people's preferences

### ✅ Conflict Resolution
- **Problem**: Not everyone can get their top choice
- **AI Solution**: Prioritizes majority while including minority preferences where possible
- **Value**: Transparent, fair reconciliation (no organizer bias)

### ✅ Decision Convergence
- **Problem**: Group can't agree on final plan
- **AI Solution**: Provides 2 clear options with trade-offs
- **Value**: Reduces negotiation from "infinite options" to "A vs B"

---

## Technical Implementation

### New Components Needed

#### 1. Trip Creation & Sharing
```python
def create_trip(
    organizer_email: str,
    theme: str,
    dates: Tuple[date, date],
    group_size: int,
    budget_range: Tuple[int, int],
) -> Dict[str, Any]:
    # Generate unique trip ID
    # Create trip record
    # Generate shareable link
    # Return: trip_id, share_link
```

#### 2. Group Voting System
```python
def submit_group_vote(
    trip_id: str,
    voter_name: str,
    vibes: List[str],
    free_text_preferences: Optional[str] = None,
) -> Dict[str, Any]:
    # Store vote
    # Update trip vote aggregation
    # Return: confirmation
```

#### 3. AI Preference Reconciliation
```python
def reconcile_preferences(
    votes: List[Dict[str, Any]],
    group_size: int,
) -> Dict[str, float]:
    # Aggregate votes (weight by voter count)
    # Identify conflicts
    # Resolve conflicts (majority + minority inclusion)
    # Return: reconciled preference profile
    # Example: {"party": 0.7, "foodie": 0.5, "relax": 0.3}
```

#### 4. Plan A/B Generation (using reconciled preferences)
```python
def generate_plan_a_b(
    reconciled_preferences: Dict[str, float],
    theme: str,
    dates: Tuple[date, date],
    budget_range: Tuple[int, int],
    venues: List[Dict[str, Any]],
) -> Tuple[List[Dict], List[Dict], Dict[str, Any]]:
    # Plan A: Premium variant
    # Plan B: Balanced variant
    # Comparison metrics
    # Return: plan_a, plan_b, comparison
```

### Data Storage (Simple Approach)

**Option 1: Session State (Demo)**
- Store votes in `st.session_state`
- Share link = trip ID in URL
- Works for demo, but not persistent

**Option 2: Simple File-Based (MVP)**
- JSON file: `trips/{trip_id}.json`
- Contains: trip params, votes, reconciled preferences, plans
- Share link: `playbook.com/trip/{trip_id}`

**Option 3: Database (Phase 2)**
- SQLite or PostgreSQL
- Proper trip/vote/user tables
- For Phase 2 scaling

---

## UI/UX Flow

### Organizer View
1. **Create Trip Page**: Current welcome page + "Create Trip" button
2. **Trip Dashboard**: Shows voting status, reconciled preferences, generate Plan A/B button
3. **Plan Comparison**: Side-by-side Plan A/B with trade-offs
4. **Itinerary Page**: Current itinerary page (for selected plan)

### Group Member View (via share link)
1. **Trip Overview**: Theme, dates, group size, current vote status
2. **Vote Page**: Select vibes (up to 3), optional free-text, submit
3. **Vote Confirmation**: "Thanks! Your preferences have been recorded"
4. **Plan A/B View** (after generation): See both plans, vote on preference (optional)

---

## What Gets Eliminated vs. Original Phase 1

### ❌ Eliminated:
- Real-time multi-user editing
- Complex conflict resolution UI
- Free-text preference parsing (for Phase 1 - can add later)
- Multi-organizer scenarios
- Preference weighting UI (handled algorithmically)

### ✅ Kept (Core AI Value):
- Preference reconciliation (algorithmic)
- Conflict resolution (algorithmic)
- Plan A/B generation
- Group voting/input
- Decision convergence workflow

---

## Why This Is Better for Phase 1

1. **Simpler**: One organizer model is standard (matches real-world)
2. **Still Demonstrates AI Value**: Preference reconciliation is the core AI step-change
3. **Lower Friction**: Link-based voting (no accounts needed)
4. **Scalable**: Can handle 5-20 person groups easily
5. **Realistic**: Matches how group trips actually get planned

---

## Phase 1 → Phase 2 Bridge

**Phase 1 Validates**:
- Do groups want AI preference reconciliation? (Yes/No)
- Is Plan A/B helpful for decision convergence? (Yes/No)
- Is link-based voting low-friction enough? (Yes/No)

**Phase 2 Adds** (if Phase 1 validates):
- Free-text preference parsing (NLP)
- More sophisticated conflict resolution UI
- Real-time updates
- Account system
- Actual API booking integration

---

## Implementation Priority

### Week 1: Core Voting System
1. Trip creation + shareable link generation
2. Group voting UI (link-based)
3. Vote aggregation logic

### Week 2: AI Reconciliation + Plan A/B
1. Preference reconciliation algorithm
2. Plan A/B generation using reconciled preferences
3. Comparison UI

### Week 3: Polish & Testing
1. Voting deadline/closure logic
2. Plan selection workflow
3. End-to-end testing

---

## Success Metrics

- ✅ Organizer can create trip and share link
- ✅ Group members can vote without accounts
- ✅ AI reconciles preferences automatically
- ✅ Plan A/B generated from reconciled preferences
- ✅ Trade-offs clearly communicated
- ✅ Group converges on final plan
