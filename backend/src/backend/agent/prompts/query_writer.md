Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the topic requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the topic.
- Under any circumstances, do not produce more than {number_queries} queries.
- Do not over-complicate queries. Only query the advanced and deep information if the topic requests it.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with this one exact key:
   - "query": A list of search queries

Examples:

Topic: John Doe
```json
{{
    "query": ["John Doe biography", "John Doe", "John Doe latest info as of August 2025"],
}}

Topic: Transformer LLM
```json
{{
    "query": ["Trasformer architecture LLM", "What is a transformer in LLM?", "How do transformers in LLM work?"],
}}

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Topic: {research_topic}