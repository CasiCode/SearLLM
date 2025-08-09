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

function getHostname(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

function getLabel(url) {
  const host = getHostname(url);
  const map = {
    'github.com': 'GitHub',
    'en.wikipedia.org': 'Wikipedia',
    'medium.com': 'Medium',
    'arxiv.org': 'arXiv',
    'npmjs.com': 'npm',
    'developer.mozilla.org': 'MDN',
    'docs.microsoft.com': 'Microsoft Docs',
    'stackoverflow.com': 'Stack Overflow'
  };
  return map[host] || host;
}

function faviconUrlPrimary(hostname) {
  return `https://icons.duckduckgo.com/ip3/${hostname}.ico`;
}

function faviconUrlFallback(hostname) {
  return `https://www.google.com/s2/favicons?sz=64&domain=${hostname}`;
}

function sourceButtonHtml(url) {
  const hostname = getHostname(url);
  const label = getLabel(url);
  const primary = faviconUrlPrimary(hostname);
  const fallback = faviconUrlFallback(hostname);

  return `
    <sl-button
      class="source-btn"
      href="${url}"
      target="_blank"
      rel="noopener noreferrer"
      variant="neutral"
      pill
      size="small">
      <img
        class="favicon"
        slot="prefix"
        src="${primary}"
        data-host="${hostname}"
        alt=""
        onerror="this.onerror=null; this.src='${fallback}'" />
      <span class="source-label">${label}</span>
      <span slot="suffix" aria-hidden="true">↗</span>
    </sl-button>
  `;
}

function buildCopyText(highlight, text, sources) {
  const lines = [];
  if (highlight) lines.push(highlight);
  if (text) lines.push('', text);

  if (sources?.length) {
    lines.push('', 'Sources:');
    lines.push(...sources.map((url, i) => `${i + 1}. ${url}`));
  }
  return lines.join('\n');
}

function updateMarkdownContent(highlight, text, sources) {
  const sourceButtons = (sources || []).map(sourceButtonHtml).join('');

  const html = `
    <h3>${highlight}</h3>

    <hr/>

    <p>${text}</p>

    <hr/>

    <h2>Sources</h2>
    <div class="source-buttons">
      ${sourceButtons}
    </div>
  `;

  markdownDisplay.innerHTML = html;
  if (copyButton) {
    copyButton.value = buildCopyText(highlight, text, sources);
  }
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