You will be given with web search results with the most recent, credible information on "{search_query}". Synthesize given information into a verifiable text artifact.

Instructions:
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings. 
- Only include the information found in the search results, don't make up any information.
- Every gathered information source must be tracked and added to summary without any changes.
- Do not make up any sources, only use the actual links provided in the context.

Format: 
- Format your response as a JSON object with this exact keys:
   - "text": Summary of the search results
   - "sources": list of links given as sources

Response example:

```json
{
    "text": "George Washington was a Founding Father and the first president of the United States, serving from 1789 to 1797. As commander of the Continental Army, Washington led Patriot forces to victory in the American Revolutionary War against the British Empire. He is commonly known as the Father of the Nation for his role in bringing about American independence.",
    "sources": ["https://en.wikipedia.org/wiki/George_Washington", "https://www.britannica.com/biography/George-Washington", "https://www.some-other-email.com/bio-of-washington"],
}
```

Research Topic:
{search_query}