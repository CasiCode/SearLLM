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
    
    await new Promise(resolve => setTimeout(resolve, 10000));
    
    searchWrapper.classList.add('moved-up');
    
    searchBar.classList.remove('glow');
    
    markdownWrapper.classList.add('visible');
    
    resetButton.classList.add('visible');
    
    updateMarkdownContent(query);
}

function updateMarkdownContent(query) {
    const mockResponse = `
        <h3><strong>Michael Jackson won at least 90 awards during his career, including 13 Grammys and 6 Brit Awards.</h3>

        <hr/>

        <p>Michael Jackson received a remarkable number of awards throughout 
        his career. He was awarded 13 Grammy Awards, including 
        prestigious honors such as the Grammy Legend Award and the Grammy 
        Lifetime Achievement Award (https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson). 
        In addition, he earned 6 Brit Awards and was honored with the 
        Diamond Award at the 2006 World Music Awards for selling over 100 
        million albums, with his album "Thriller" alone surpassing 104 
        million copies sold worldwide 
        (https://simple.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson). 
        Overall, Michael Jackson accumulated at least 90 wins and 82 
        nominations across various awards from multiple organizations 
        (https://tylerturneymjhdp.weebly.com/achievementsawards.html; 
        https://michael-jackson.fandom.com/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson; 
        https://www.imdb.com/name/nm0001391/awards/).</p>

        <hr/>
        
        <h2>Sources</h2>
        <ul>
            <li><a href=https://tylerturneymjhdp.weebly.com/achievementsawards.html></a></li>
            <li><a href=https://michael-jackson.fandom.com/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson></a></li>
            <li><a href=https://simple.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson></a></li>
            <li><a href=https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Michael_Jackson></a></li>
            <li><a href=https://www.imdb.com/name/nm0001391/awards/></a></li>
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