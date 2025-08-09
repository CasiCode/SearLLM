const searchBar = document.getElementById('searchBar');
const searchWrapper = document.getElementById('searchWrapper');
const searchContainer = document.getElementById('searchContainer');
const markdownWrapper = document.getElementById('markdownWrapper');
const markdownDisplay = document.getElementById('markdownDisplay');
const copyButton = document.getElementById('copyButton');
const shareBtn = document.getElementById('shareButton');


const shareState = {
	query: '',
	highlight: '',
	text: '',
	source_documents: []
};


searchBar.addEventListener('keypress', (e) => {
	if (e.key === 'Enter' && searchBar.value.trim()) {
		performSearch(searchBar.value);
	}
});

async function performSearch(query) {
	searchBar.classList.add('glow');
	searchBar.blur();

	const jsonResponse = await getApiResponse(
		Date.now().toString(),
		Date.now().toString(),
		query
	);

	shareState.query = query;
	shareState.highlight = jsonResponse?.highlight || '';
	shareState.text = jsonResponse?.message || '';
	shareState.source_documents = jsonResponse?.source_documents || [];

	searchWrapper.classList.add('moved-up');
	searchBar.classList.remove('glow');

	markdownWrapper.classList.add('visible');
	searchContainer?.classList.add('has-result');

	updateMarkdownContent(shareState.highlight, shareState.text, shareState.source_documents);
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
	searchContainer?.classList.remove('has-result');

	copyButton.classList.remove('copied');
	
	searchBar.value = '';
	searchBar.focus();

	shareState.query = '';
	shareState.highlight = '';
	shareState.text = '';
	shareState.source_documents = [];
	
	setTimeout(() => {
		markdownDisplay.innerHTML = '';
	}, 600);
}

document.addEventListener('DOMContentLoaded', () => {
	const m = location.pathname.match(/^\/s\/([^/?#]+)$/);
	if (m) {
		const slug = decodeURIComponent(m[1]);
		hydrateFromSlug(slug);
	}

	const updateShareEnabled = () => {
		const hasContent = (markdownDisplay?.textContent || '').trim().length > 0;
		if (shareBtn) shareBtn.disabled = !hasContent;
	};

	const mo = new MutationObserver(updateShareEnabled);
	if (markdownDisplay) {
		mo.observe(markdownDisplay, { childList: true, subtree: true, characterData: true });
	}

	updateShareEnabled();

	shareBtn?.addEventListener('click', async () => {
		const { query, highlight, text, source_documents } = shareState;
		if (!highlight || !text) return;

		try {
		shareBtn.loading = true;
		shareBtn.disabled = true;

		const res = await fetch('/api/proxy-share', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ query, highlight, text, source_documents })
		});

		const data = await res.json().catch(() => ({}));

		if (res.ok && data?.slug) {
			try {
			await navigator.clipboard.writeText(`${location.origin}/s/${data.slug}`);
			console.log('Share URL copied to clipboard:', `${location.origin}/s/${data.slug}`);
			} catch (e) {
			console.warn('Could not copy share URL:', e);
			}
		}
		} catch (err) {
		console.error('Share request failed:', err);
		} finally {
		shareBtn.loading = false;
		shareBtn.disabled = false;
		}
	});
});


async function hydrateFromSlug(slug) {
	try {
		markdownDisplay.innerHTML = '<p>Loading shared result…</p>';
		searchWrapper.classList.add('moved-up');
		markdownWrapper.classList.add('visible');
		searchContainer?.classList.add('has-result');

		const res = await fetch('/api/proxy-share-data', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ slug })
		});

		if (!res.ok) {
			throw new Error(`Failed to load shared result (${res.status})`);
		}

		const data = await res.json();

		const query = data.query || '';
		const highlight = data.highlight || '';
		const text = data.text || data.message || '';
		const sourcesRaw = data.source_documents || data.sources || [];
		const sources = Array.isArray(sourcesRaw)
		? sourcesRaw
			.map(s => (typeof s === 'string' ? s : (s?.url || s?.link || s?.href || '')))
			.filter(Boolean)
		: [];

		shareState.query = query;
		shareState.highlight = highlight;
		shareState.text = text;
		shareState.source_documents = sources;

		if (query) searchBar.value = query;
		updateMarkdownContent(highlight, text, sources);

		try {
			document.title = `SearLLM — ${highlight || 'Shared result'}`;
		} catch {}
	} catch (err) {
		console.error('hydrateFromSlug error:', err);
		markdownDisplay.innerHTML = '<p>Shared result not found or expired.</p>';
		searchWrapper.classList.add('moved-up');
		markdownWrapper.classList.add('visible');
	}
}