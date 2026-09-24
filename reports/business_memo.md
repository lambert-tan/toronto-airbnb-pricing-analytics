# Business Memo: What Drives Airbnb Nightly Prices in Toronto?

**To:** Toronto Airbnb Hosts and Property Managers  
**From:** Lambert Tan  
**Subject:** Pricing evidence from 15,332 Toronto listings

## Executive summary

I analyzed 15,332 Toronto listings from the November 2025 Inside Airbnb snapshot to examine which observable listing characteristics are most closely associated with nightly price. The final log-price model explains about 61.8% of variation in the test sample.

The strongest pattern is not simply “downtown costs more.” Property format matters first. Entire homes are associated with substantially higher nightly prices than private rooms, while a shared bathroom is associated with a sizeable discount. Distance from downtown still matters after these characteristics are controlled for, but the estimated effect is smaller and gradual.

For hosts, this means that a useful pricing comparison should start with structurally similar listings. Neighbourhood averages alone can mix together properties that are not genuinely comparable.

## Findings

An entire home is associated with an estimated **43.8% higher nightly price** than a private room, holding the other included variables constant. A shared bathroom is associated with an estimated **21.0% lower price**.

Location remains relevant. Each additional kilometre from the downtown reference point is associated with approximately a **2.7% decrease** in nightly price. This is meaningful across larger distances, but it does not outweigh major differences in property format.

The smaller operational variables have more modest relationships with price. Instant booking is associated with roughly a **2.4% premium**, while each additional amenity is associated with about **0.4%**. Superhost status and host experience were considered during model development but did not remain in the final specification after the other listing characteristics were taken into account.

## Pricing implications

I would use the results in two stages. First, establish a benchmark from listings with a similar room type, bathroom arrangement, capacity, and number of bedrooms and bathrooms. Second, adjust that benchmark for location and smaller operational differences such as instant booking and amenity count.

This also changes how I would interpret Superhost status. The analysis does not provide evidence for using the badge itself as a direct nightly-rate premium. It may still affect guest trust, booking conversion, or occupancy, but those outcomes are not measured here.

## Limits of the analysis

The estimates describe conditional associations in one cross-sectional snapshot; they are not causal effects. The data do not directly capture seasonality, occupancy, booking conversion, guest preferences, event demand, or current competitor inventory. Several size variables are also correlated, so their coefficients are best interpreted together rather than as isolated effects.

The next extension I would prioritize is repeated listing data combined with a demand or occupancy measure. That would allow the analysis to move beyond explaining cross-sectional price differences and toward a more realistic dynamic pricing problem.
