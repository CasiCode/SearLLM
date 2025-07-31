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
    
    await new Promise(resolve => setTimeout(resolve, 10000));
    
    searchWrapper.classList.add('moved-up');
    
    searchBar.classList.remove('glow');
    
    markdownWrapper.classList.add('visible');
    
    resetButton.classList.add('visible');
    
    updateMarkdownContent(query);
    
    searchBar.blur();
}

function updateMarkdownContent(query) {
    const mockResponse = `
        <h1>Search Results for: "${query}"</h1>
        <p>Here's what I found about <strong>${query}</strong>:</p>
        
        <h2>Overview</h2>
        <p>This is a comprehensive answer about your search query. In a real implementation, this content would come from your backend API or search service.</p>
        
        <h2>Key Points</h2>
        <ul>
            <li>First important point about ${query}</li>
            <li>Second relevant detail</li>
            <li>Third key insight</li>
        </ul>
        
        <h2>Additional Information</h2>
        <p>You can integrate this with any search API or knowledge base to provide real answers. The animation creates a smooth transition from search to results.</p>
        
        <p><em>Last updated: ${new Date().toLocaleDateString()}</em></p>
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