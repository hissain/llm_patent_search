prompt_keywords = r"""
You are an expert in generating precise and relevant keywords for prior art searches in the Google Patent Database based on a given idea. Your task is to extract technical terms and related synonyms to ensure comprehensive coverage of the concept.

**IDEA:** {topic}

**Instructions:**
1. Provide the keywords as a single, comma-separated list.
2. Include synonyms or variations of terms where applicable.
3. Focus on technical terms and industry-specific jargon.
4. Avoid unnecessary words, comments, or explanations.

**Example Output:**
solar energy, nanotechnology, efficient energy conversion, photovoltaic systems, solar cells, renewable energy
"""

prompt_query = r"""
You are an expert in constructing advanced query strings for searching the Google Patent Database effectively. Your task is to create query strings based on the provided idea and keywords, ensuring high precision and recall.

**IDEA:** {topic}

**Instructions:**
1. Generate at least three distinct, complex query strings.
2. Use Boolean operators (AND, OR, NOT), proximity operators (SAME, ADJ, NEAR), parentheses for grouping, and wildcard symbols (*) for variations.
3. Distribute the keywords effectively across the queries to maximize coverage.
4. Avoid unnecessary words, comments, or explanations.
5. Focus on constructing queries suitable for a patent database search.
6. Query strings should be returned comma seperated.

**Example Output:**
((solar* OR photovoltaic*) AND ("energy conversion" SAME efficient)) AND (nanotechnology OR "nano material"),
((wearable AND "noise cancellation") OR ("adaptive filtering" NEAR headphones)) AND NOT ("legacy systems"),
((renewable* OR "green energy") AND (grid SAME independent)) AND ("battery storage" OR "energy harvesting")
"""
