const searchBar = document.getElementById('searchBar');
const searchWrapper = document.getElementById('searchWrapper');
const markdownWrapper = document.getElementById('markdownWrapper');
const markdownDisplay = document.getElementById('markdownDisplay');
const resetButton = document.getElementById('resetButton');
const copyButton = document.getElementById('copyButton');


searchBar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && searchBar.value.trim()) {
        performSearch(searchBar.value);
    }
});

async function performSearch(query) {
    searchBar.classList.add('glow');
    searchBar.blur();
    
    jsonResponse = await getApiResponse(
        session_id=Date.now().toString(),
        user_id=Date.now().toString(),
        message=query,
    );

    searchWrapper.classList.add('moved-up');
    
    searchBar.classList.remove('glow');
    
    markdownWrapper.classList.add('visible');
    resetButton.classList.add('visible');
    
    updateMarkdownContent(jsonResponse.highlight, jsonResponse.message, jsonResponse.source_documents);
}

async function performSearchWithButton() {
    performSearch(searchBar.value)
}

async function getApiResponse(session_id, user_id, message) {
    const data = {
        session_id: session_id,
        user_id: user_id,
        message: message
    };

    try {
        console.log(JSON.stringify(data));

        const response = await fetch('/api/proxy-query', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            console.error('Failed to get an OK response.');
            return;
        }

        const jsonResponse = await response.json();
        return jsonResponse;
    }
    catch (error) {
        console.log(error);
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

async function copyMarkdownContent() {
    const copyButton = document.getElementById('copyButton');
    const markdownContent = document.getElementById('markdownDisplay');
    
    const textContent = markdownContent.innerText;
    
    try {
        await navigator.clipboard.writeText(textContent);
        
        copyButton.classList.add('copied');
        
        setTimeout(() => {
            copyButton.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
}

function resetSearch() {
    searchWrapper.classList.remove('moved-up');
    markdownWrapper.classList.remove('visible');
    resetButton.classList.remove('visible');

    copyButton.classList.remove('copied');
    
    searchBar.value = '';
    searchBar.focus();
    
    setTimeout(() => {
        markdownDisplay.innerHTML = '';
    }, 600);
}