Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the topic requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the topic.
- Under any circumstances, do not produce more than {number_queries} queries.
- Do not over-complicate queries. Only query the advanced and deep information if the topic requests it.
- If the topic is a term, the query should ask for its definition.
- If the topic is a name, the query should ask for who or what it is.
- The current date is {current_date}.

Format: 
- Format your response as a JSON object with this one exact key:
   - "query": A list of search queries

Examples:

Topic: Albert Einstein
```json
{{
    "query": ["Albert Einstein's biography and career", "Who is Albert Einstein?"],
}}

Topic: Transformer LLM
```json
{{
    "query": ["What is a transformer in LLM?"],
}}

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Topic: Latest OpenAI model
```json
{{
    "query": ["What is the latest OpenAI model as of {current_date}?", "OpenAI latest news as of {current_date}"],
}}
```

Topic: What happened in London today?
```json
{{
    "query": ["Latest events in London {current_date}", "London news {current_date}"],
}}
```

Topic: {research_topic}