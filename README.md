# homebuyerswi-funnel

Multi branch seller qualification funnel for **Kustom Property Solutions** (homebuyerswi.com), built on the
same architecture as the MaliHaus funnel: six situations, multi select, a merged question queue, combination
logic, a lead tier engine, and a contact form at the end.

Two pages, both self contained, no build step.

| File | What it is |
|---|---|
| `index.html` | The seller funnel |
| `lead-example.html` | What lands in the CRM, three worked sample leads |

## Branding

Everything visual is pulled from www.homebuyerswi.com, read 2026-09-10, not invented.

| Token | Value | Source |
|---|---|---|
| Brand blue | `#0CA0DA` | their `--color-brand-primary` |
| Blue darker | `#086B91` | their `--color-brand-primary-darker` |
| Action orange | `#FF8800` | their `--color-button` |
| Orange darker | `#B35F00` | their `--color-button-darker` |
| Secondary dark | `#065A79` | their `--color-brand-secondary-dark` |
| Near black | `#021D27` | their `--color-brand-secondary-darker` |
| Body text | `#373A3C` | their `--body-color` |
| Typeface | Source Sans 3 | their `--font-headings` and `--font-primary` are Source Sans Pro |
| Logo | `img/logo-blue.svg` | their own `Logo-Blue-Version.svg` |
| Favicon | `img/favicon.png` | their own apple touch icon |

The six situation hues are deliberately chosen to leave orange alone, because orange is the client's action
colour and has to stay unambiguous as "this is the button".

## Branch to ad campaign map

Read from Kustom's live ChatGPT Ads account on 2026-09-06.

| Branch | Campaign |
|---|---|
| `deadline` | `Kustom_SoutheastWI_ChatGPTAds_UrgentExit`, plus the Foreclosure and Tax Delinquency groups |
| `condition` | `Kustom_SoutheastWI_ChatGPTAds_ProblemProperty`, plus Fire & Water Damage |
| `moving` | `Kustom_SoutheastWI_ChatGPTAds_LifeTransition` |
| `comparing` | `Kustom_SoutheastWI_ChatGPTAds_LeadGen_90Day` |
| `inherited`, `rental` | no dedicated campaign today |

An ad can deep link straight into its own branch with `?s=deadline`, `?s=condition` and so on, so the
seller never re-picks something the ad already told us.

## What is deliberately NOT on the page

* No price, no range, no percentage, and no "we pay X% of market". Any figure before a walkthrough is a
  guess, and a guess that moves down later is exactly what sellers distrust about this industry.
* No deal structure is named or ranked. Kustom buys with cash; nothing here should read as a quote or as an
  offer of terms nobody has approved.
* No channel mechanics, ad specs, budgets or UTM tables. That is the agency's side, not the seller's.

## Before this runs on paid traffic

1. **Wire `submitLead()`.** It is front end only right now and marked `WIRE THIS UP` in `index.html`. It
   builds the payload and logs it to the console; nothing is POSTed anywhere. Do not point ad spend at this
   until a real test submission has been seen landing in the CRM.
2. **Point `getGuide()` at a real PDF.** It currently fires a placeholder alert.
3. **Confirm the SMS consent wording.** The consent block copies the wording from the two live forms on
   www.homebuyerswi.com verbatim, so the funnel makes no claim the client's own site does not already make.
   Confirm it against the current A2P registration before launch, and do not reword it unilaterally.
4. **Decide on the assistant.** The scripted chat panel is on by default and labelled as a demo. Set
   `ASSISTANT_ON = false` near the top of the first `<script>` in `index.html` to remove it completely.
5. **Check the geography rule.** Unlike a national buyer, this funnel disqualifies "Outside Wisconsin" and
   says so honestly rather than collecting the form. Widen `COMMON.location` and `routeOut()` if Kustom's
   footprint changes.

## Hosting note

`homebuyerswi.com` is Kustom's primary website and `options.homebuyerswi.com` is the separate Lovable funnel.
This repo is a third, distinct asset and does not replace either of them. Do not point an existing hostname
at it without deciding that deliberately.
