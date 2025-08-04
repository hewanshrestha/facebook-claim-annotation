## Task 1: Claim Detection

Select `Claim` if the image–text pair makes a verifiable assertion that can be checked using reliable external sources (e.g., news outlets, government websites, official reports), and it includes at least one of the following:

`Note`: **⚠️ A Claim must be a clear, fact-checkable assertion, not just anything you can Google.**

• Local Context: Mentions of country-specific places, political parties, events, or administrative units.

• Who / What / When / Where: Statements about specific individuals, organizations, dates, or locations.

• Laws, Procedures, or Policies: References to rules, regulations, or official processes.

• Numbers or Statistics: Quantitative data like counts, budgets, or turnout figures.

• Verifiable Predictions: Forecasts or claims about future events.

• Image-Based Claims: Assertions about the image itself, especially if it depicts something country-specific.

• Text Overlays or Memes: When memes or image text contain checkable facts.

Label as `No Claim` if:

• Generic or Promotional Statements

• Generic Definitions or Explanations

• Pure opinion, emotion, or sarcasm

• Hashtags, name mentions, or vague references

• Insufficient detail for verification


## Task 2: Checkworthiness Detection

For items labeled `Claim`, select `Check-worthy` if the claim contains one or more of the following impact-driven or urgency indicators — especially in public, political, or high-risk content:

`Check-worthy` = **A claim a fact-checker should verify because it could mislead or impact the public.**

• Harmful or Defamatory Content: Targets individuals, groups, or communities with accusations or hate.

• Urgent/Breaking News: Tied to disasters, violence, protests, or immediate developments.

• Public-Interest Value: Affects a large population (e.g., health, economy, education, environment).

• Recent Laws, Court Rulings, Policies: Especially if newly introduced or controversial.

• Image-Text Mismatch or Sensationalism: Shocking images used misleadingly or emotionally.

• Emotive or Panic-Inducing Language: Words meant to provoke fear, anger, or mass reaction.

• Conspiracies or Scandals: Claims that hint at cover-ups, secret dealings, or major plots.

• Repost or Source Alerts: Viral resharing, copied content, or second-hand sources.

Label as `Not Check-worthy` if:

• The claim is fact-checkable but low-impact, benign, or not socially important.

• It lacks signs of urgency, virality, or public consequence.

• It’s personal or trivial.
