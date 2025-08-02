## Task 1: Claim Detection

Select **Claim** if the image–text pair contains a verifiable assertion that can be confirmed via external sources and includes at least one of the following elements:

• **Local Context**: References to country-specific entities, events, or administrative units. 

• **Who/What/When/Where**: Specific individuals, organizations, dates, or locations within the country.

• **Procedures, Laws, Policies**: Citations of country-specific legislation, government orders, or processes.

• **Numbers and Statistics**: Local figures such as case counts, budget amounts, or turnout numbers.

• **Verifiable Predictions**: Forecasts about monsoons, election outcomes, or economic indicators affecting the country.

• **Image References**: Claims about the content of the image, especially when depicting country-specific contexts.

• **Text Overlays & Memes**: Claims embedded in image text overlays or memes.

Label as **No Claim** if none of the above criteria are met or the text is purely opinion, anecdote, or greeting without verifiable content.


## Task 2: Checkworthiness Detection

For items labeled Claim in Task 1, select **Check-worthy** if the claim exhibits one or more of the following properties—tailored to high-impact Nepali Facebook content:

• **Harmful or Defamatory Content**: Attacks or rumors against individuals, parties, ethnic groups, or communities that can incite social discord.

• **Urgent/Breaking News**: Statements about active crises, protests, disasters, or policy shifts.

• **Public-Interest Value**: Claims affecting large populations—health alerts, educational reforms, constitutional amendments.

• **Recent-Law & Official Rulings**: References to newly enacted laws, Supreme Court decisions, treaties influencing the citizens.

• **Visual Sensationalism & Mismatch**: Dramatic images (collapsed bridges, riots) paired with urgent text or when image content contradicts text claims.

• **Emotive or Panic-Inducing Language**: Posts evoking fear or outrage.

• **Conspiracy/Scandal Indicators**: Unverified plots or scandals.

• **Repost or Source Alerts**: Mentions of viral chains or second-hand sources that require origin tracing.

Label as **Not Check-worthy** if the claim lacks these high-impact or urgency cues despite being verifiable.