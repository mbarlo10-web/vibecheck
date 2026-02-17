# Phase 1 Implementation Plan: Bridging the Gap

## Overview
This plan addresses the gap between current VibeCheck functionality and the Phase 1 proposal, focusing on:
1. **Plan A vs Plan B** generation (two ranked itinerary options)
2. **API Integration Feasibility Assessment**

---

## Part 1: Plan A vs Plan B Implementation

### Current State
- App generates **one itinerary** using deterministic logic
- Uses `pick_best_rotating()` for venue selection
- No trade-off comparison or alternative options

### Proposed Changes

#### 1.1 Dual Itinerary Generation Strategy

**Approach**: Generate two variants with different trade-off profiles:

- **Plan A: "Premium Experience"**
  - Prioritizes higher `price_tier` venues (3-4)
  - Favors "luxury" vibes
  - More upscale dining/nightlife
  - Fewer compromises on venue quality

- **Plan B: "Balanced & Value"**
  - Mixes mid-range venues (price_tier 2-3)
  - Emphasizes "balanced" vibes
  - More variety across price points
  - Better budget alignment

**Implementation**:
```python
def build_itinerary_variant(
    venues: List[Dict[str, Any]],
    theme: str,
    vibes: List[str],
    arrival: date,
    departure: date,
    team: str,
    variant: str = "premium",  # "premium" or "balanced"
) -> List[Dict[str, Any]]:
    # Same structure as current build_itinerary()
    # But adjust venue selection logic:
    # - Premium: prefer higher price_tier, luxury vibes
    # - Balanced: prefer mid-range, balanced vibes
```

#### 1.2 UI Changes Required

**Welcome Page**:
- Keep "Generate Itinerary" button
- After generation, show **two tabs or side-by-side**: "Plan A" and "Plan B"
- Add comparison summary showing key differences

**Itinerary Page**:
- **Tab 1: Plan A** (with tagline like "Premium Experience")
- **Tab 2: Plan B** (with tagline like "Balanced & Value")
- **Comparison View**: Side-by-side or toggle showing:
  - Estimated budget difference
  - Venue quality differences
  - Key trade-offs (e.g., "Plan A: More luxury venues, +$200/person" vs "Plan B: More variety, stays within budget")

**Session State Updates**:
```python
st.session_state.setdefault("itinerary_plan_a", [])
st.session_state.setdefault("itinerary_plan_b", [])
st.session_state.setdefault("selected_plan", None)  # "A" or "B"
st.session_state.setdefault("plan_comparison", {})
```

#### 1.3 Trade-off Calculation

Create a function to generate comparison metrics:
```python
def compare_plans(plan_a: List[Dict], plan_b: List[Dict], venues: List[Dict]) -> Dict[str, Any]:
    # Calculate:
    # - Average price_tier per plan
    # - Venue count differences
    # - Estimated budget impact
    # - Key venue differences (luxury vs mid-range)
    return {
        "plan_a_avg_price": ...,
        "plan_b_avg_price": ...,
        "budget_difference": ...,
        "key_differences": [...]
    }
```

#### 1.4 Files to Modify

1. **`app.py`**:
   - Add `build_itinerary_variant()` function
   - Modify "Generate Itinerary" button to create both Plan A and Plan B
   - Update `render_itinerary()` to handle two plans with tabs
   - Add comparison UI component

2. **`orchestrator.py`** (integrate scoring):
   - Use `rank_venues()` to score venues
   - Apply different weights for Plan A vs Plan B
   - Plan A: Higher weight on `price_tier` and `luxury` vibe
   - Plan B: Higher weight on `balanced` vibe and budget alignment

---

## Part 2: API Integration Feasibility Assessment

### Reality Check: What's Actually Possible?

#### 2.1 APIs That Are Feasible (with caveats)

**✅ Ticketmaster / Event APIs**
- **Status**: Public API available
- **Requirements**: API key registration (free tier available)
- **Capabilities**: Search events, get ticket links, pricing
- **Limitations**: Cannot actually purchase tickets via API (requires redirect to Ticketmaster)
- **Phase 1 Approach**: Generate deep links with pre-filled event details
- **Phase 2 Approach**: OAuth integration for booking (requires partnership)

**✅ Resy API**
- **Status**: Public API available
- **Requirements**: API key + OAuth for user accounts
- **Capabilities**: Search restaurants, check availability, create reservations
- **Limitations**: Requires user to authenticate with Resy account
- **Phase 1 Approach**: Deep links to Resy with pre-filled restaurant/date/time
- **Phase 2 Approach**: OAuth flow + actual booking (requires Resy partnership)

**✅ GolfNow API**
- **Status**: Partner API (not publicly documented)
- **Requirements**: Business partnership/approval
- **Capabilities**: Search tee times, book rounds
- **Limitations**: Requires partnership agreement
- **Phase 1 Approach**: Deep links to GolfNow with pre-filled course/date
- **Phase 2 Approach**: Partnership + API integration

#### 2.2 APIs That Are Challenging

**⚠️ OpenTable**
- **Status**: No public API for third-party booking
- **Requirements**: Enterprise partnership only
- **Reality**: OpenTable does not allow third-party booking aggregation
- **Phase 1 Approach**: Deep links only ("Book via OpenTable" → opens OpenTable website)
- **Phase 2 Approach**: Enterprise partnership (unlikely for startup)

**⚠️ Uber / Lyft**
- **Status**: APIs exist but require business accounts
- **Requirements**: OAuth + business account approval
- **Capabilities**: Request rides, estimate costs
- **Limitations**: Cannot book rides for others without business account
- **Phase 1 Approach**: Deep links with destination pre-filled
- **Phase 2 Approach**: Business account + API integration (complex)

**⚠️ Restaurant Direct APIs**
- **Status**: Varies by restaurant
- **Reality**: Most restaurants use Resy/OpenTable, not direct APIs
- **Phase 1 Approach**: Deep links to restaurant booking pages
- **Phase 2 Approach**: Custom integrations per restaurant (not scalable)

#### 2.3 Recommended Phase 1 Approach

**"VibeCheck Will Handle Booking" Messaging Strategy**:

1. **For Phase 1 (Planning Focus)**:
   - Keep messaging: "VibeCheck will book via [Platform]"
   - **Actual implementation**: Generate deep links with pre-filled details
   - User clicks → redirected to booking platform with details pre-filled
   - Example: `https://www.resy.com/restaurants/[venue]?date=2026-02-20&time=19:30&covers=6`

2. **Booking Codes / Instructions**:
   - For venues without APIs: Provide booking codes or instructions
   - Example: "Call [venue] and mention VibeCheck booking code: VC-ABC123"

3. **Stripe Payment Integration** (already implemented):
   - Use for "plan lock" fee ($99)
   - Can be extended for actual booking deposits in Phase 2

#### 2.4 Phase 2 API Integration Roadmap

**Priority Order**:
1. **Ticketmaster** (easiest, public API)
2. **Resy** (public API, requires OAuth)
3. **GolfNow** (requires partnership)
4. **Uber/Lyft** (requires business account)
5. **OpenTable** (unlikely without enterprise partnership)

**Implementation Strategy**:
- Start with deep links (Phase 1)
- Validate demand and user behavior
- Build partnerships for Phase 2 actual booking
- Focus on platforms with public APIs first

---

## Implementation Steps

### Step 1: Plan A/B Generation (Week 1)
1. Create `build_itinerary_variant()` function
2. Integrate `orchestrator.py` scoring logic
3. Generate both plans on "Generate Itinerary" click
4. Store both in session state

### Step 2: UI for Plan Comparison (Week 1-2)
1. Add tab UI for Plan A vs Plan B
2. Create comparison summary component
3. Add "Select Plan" functionality
4. Update itinerary rendering to show selected plan

### Step 3: Deep Link Generation (Week 2)
1. Create `generate_booking_links()` function
2. Generate deep links for Resy, Ticketmaster, GolfNow
3. Update booking text to include clickable links
4. Test deep links with real venues

### Step 4: Testing & Refinement (Week 2-3)
1. Test Plan A/B generation with different themes/vibes
2. Validate trade-off calculations
3. Test deep links across platforms
4. Gather user feedback on comparison UX

---

## Success Metrics

### Plan A/B:
- ✅ Users can compare two itinerary options
- ✅ Trade-offs are clearly communicated
- ✅ Users can select preferred plan
- ✅ Selected plan becomes the "active" itinerary

### API Integration (Phase 1):
- ✅ Deep links work for major platforms
- ✅ Booking messaging is clear and accurate
- ✅ Users understand VibeCheck handles coordination, not actual booking (yet)
- ✅ Foundation laid for Phase 2 actual API integration

---

## Notes

- **Phase 1 Scope**: Focus on planning and decision convergence, not actual booking execution
- **API Reality**: Most booking APIs require partnerships; deep links are Phase 1 solution
- **User Expectations**: Set clear expectations that "VibeCheck will book" means coordination + deep links, not automated booking (yet)
- **Phase 2 Bridge**: Phase 1 validates demand → Phase 2 builds partnerships → Phase 2 enables actual API booking
