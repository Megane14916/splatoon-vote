document.addEventListener('DOMContentLoaded', () => {
    const rankingList = document.getElementById('ranking-list');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loader = document.getElementById('loader');
    
    let currentOffset = 0; // 現在読み込んでいる順位
    let isLoading = false;

    // ランキングデータをサーバーから取得する関数
    async function fetchRankingData() {
        if (isLoading) return;
        isLoading = true;
        
        loader.style.display = 'block';
        loadMoreBtn.disabled = true;

        try {
            const response = await fetch(`/api/ranking_data?offset=${currentOffset}`);
            const data = await response.json();

            if (data.length > 0) {
                appendRankingItems(data);
                currentOffset += data.length;
            } else {
                // これ以上データがない場合
                loadMoreBtn.textContent = 'すべてのブキを読み込みました';
                loadMoreBtn.disabled = true;
            }
        } catch (error) {
            console.error('ランキングデータの取得に失敗しました:', error);
            loadMoreBtn.textContent = 'エラーが発生しました';
        } finally {
            isLoading = false;
            loader.style.display = 'none';
            if (loadMoreBtn.textContent !== 'すべてのブキを読み込みました') {
                loadMoreBtn.disabled = false;
            }
        }
    }

    // 取得したデータをHTMLに変換して追加する関数
    function appendRankingItems(items) {
        items.forEach((item, index) => {
            const rank = currentOffset + index + 1;

            const rankItem = document.createElement('div');
            rankItem.className = 'ranking-item';

            let rankText = rank;
            let rankClass = '';

            if (rank === 1) {
                rankClass = 'rank-1st';
                rankText = `${rank}<span class="rank-medal gold"></span>`;
            } else if (rank === 2) {
                rankClass = 'rank-2nd';
                rankText = `${rank}<span class="rank-medal silver"></span>`;
            } else if (rank === 3) {
                rankClass = 'rank-3rd';
                rankText = `${rank}<span class="rank-medal bronze"></span>`;
            }

            rankItem.innerHTML = `
                <div class="rank-col ${rankClass}">
                <span class="rank-number-with-medal">${rankText}</span>
                </div>
                <div class="weapon-col">
                <img src="/static/images/main/${item.main.image}" alt="${item.main.name}" class="main-icon">
                <span class="weapon-name">${item.main.name}</span>
                <div class="weapon-details">
                <img src="/static/images/sub/${item.sub.image}" alt="${item.sub.name}" class="sub-icon">
                <img src="/static/images/special/${item.special.image}" alt="${item.special.name}" class="special-icon">
                </div>
                </div>
                <div class="votes-col">${item.vote_count} 票</div>
            `;
            rankingList.appendChild(rankItem);
        });
    }

    // --- イベントリスナー ---
    loadMoreBtn.addEventListener('click', fetchRankingData);

    // --- 初期読み込み ---
    fetchRankingData();
});