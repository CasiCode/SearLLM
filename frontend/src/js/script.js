const searchBar = document.getElementById('searchBar');
const searchWrapper = document.getElementById('searchWrapper');
const markdownWrapper = document.getElementById('markdownWrapper');
const markdownDisplay = document.getElementById('markdownDisplay');
const loading = document.getElementById('loading');
const resetButton = document.getElementById('resetButton');

searchBar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && searchBar.value.trim()) {
        performSearch(searchBar.value);
    }
});

async function performSearch(query) {
    searchBar.classList.add('glow');
    searchBar.blur();
    
    jsonResponse = await getApiResponse(
        session_id=crypto.randomUUID(),
        user_id=parseInt(crypto.randomUUID().replace(/-/g, ''), 16),
        message=query,
    );

    searchWrapper.classList.add('moved-up');
    
    searchBar.classList.remove('glow');
    
    markdownWrapper.classList.add('visible');
    resetButton.classList.add('visible');
    
    updateMarkdownContent(jsonResponse.highlight, jsonResponse.message, jsonResponse.source_documents);
}

async function getApiResponse(session_id, user_id, message) {
    const data = {
        session_id: session_id,
        user_id: user_id,
        message: message
    };

    try {
        const response = await fetch('http://searxng:8000/queries/query', 
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "SearLLM-API-token": process.env.SEARLLM_API_TOKEN
                },
                body: JSON.stringify(data)
            }
        );

        if (!response.ok) {
            throw new Error("Network response was not OK");
        }

        const jsonResponse = await response.json();
        return jsonResponse
    }
    catch (error) {
        console.log(error)
    }
}

function updateMarkdownContent(highlight, text, sources) {
    let concatenatedSources = ''
    sources.forEach(link => {
        concatenatedSources += `<li><a href=${link}></a></li>\n`;
    });

    const mockResponse = `
        <h3>${highlight}</h3>

        <hr/>

        <p>${text}</p>

        <hr/>
        
        <h2>Sources</h2>
        <ul>
            ${concatenatedSources}
        </ul>
    `;
    
    markdownDisplay.innerHTML = mockResponse;
}

function resetSearch() {
    searchWrapper.classList.remove('moved-up');
    markdownWrapper.classList.remove('visible');
    resetButton.classList.remove('visible');
    
    searchBar.value = '';
    searchBar.focus();
    
    setTimeout(() => {
        markdownDisplay.innerHTML = '';
    }, 600);
}