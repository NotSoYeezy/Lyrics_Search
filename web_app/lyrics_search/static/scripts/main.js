const body = document.body;
const modal = document.getElementById('modal');
const closeModal = document.getElementById('close-modal');
const searchButton = document.getElementById('search-button');
const searchBar = document.getElementById('search-bar');

closeModal.addEventListener('click', () => {
    modal.classList.add('hidden');
});

searchButton.addEventListener('click', performSearch);
searchBar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

function performSearch() {
    const query = searchBar.value.trim();
    if (!query) return;

    const results = document.getElementById('results');
    results.innerHTML = '<div class="text-center py-4 text-white">Wyszukiwanie...</div>';

    fetch('/query_lyrics', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Błąd serwera');
        }
        return response.json();
    })
    .then(data => {
        if (data.results && data.results.length > 0) {
            displayResults(data.results);
        } else {
            results.innerHTML = '<div class="text-center py-4 bg-white dark:bg-gray-800 rounded-lg">Nie znaleziono wyników</div>';
        }
    })
    .catch(error => {
        console.error('Błąd:', error);
        results.innerHTML = `<div class="text-center py-4 bg-white dark:bg-gray-800 rounded-lg text-red-500">Wystąpił błąd: ${error.message}</div>`;
    });
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    results.forEach(song => {
        const snippetLyrics = song.lyrics.substring(0, 60) + '...';

        const resultElement = document.createElement('div');
        resultElement.className = 'p-4 mb-2 border-b border-gray-300 cursor-pointer bg-white dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700';
        resultElement.onclick = () => showLyrics(song.title, song.lyrics, song.artist);

        resultElement.innerHTML = `
            <div class='flex items-center'>
                <div class='w-12 h-12 rounded mr-4 bg-gray-300 dark:bg-gray-600 flex items-center justify-center'>
                    <span class="text-lg font-bold">${song.title.charAt(0)}</span>
                </div>
                <div>
                    <h3 class='text-lg font-semibold'>${song.title}</h3>
                    <p class='text-sm text-gray-500 dark:text-gray-300'>${song.artist}</p>
                    <p class='text-sm text-gray-400'>${snippetLyrics}</p>
                </div>
            </div>
        `;

        resultsDiv.appendChild(resultElement);
    });
}

function showLyrics(title, lyrics, artist) {
    document.getElementById('modal-title').textContent = `${title} - ${artist}`;
    document.getElementById('modal-lyrics').textContent = lyrics;
    modal.classList.remove('hidden');
}