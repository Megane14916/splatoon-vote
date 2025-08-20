document.addEventListener('DOMContentLoaded', () => {
    // --- 定数とDOM要素の取得 ---
    const MAX_VOTES_PER_DAY = 10;
    const voteButtons = document.querySelectorAll('.vote-button');
    const votesRemainingElement = document.getElementById('votes-remaining');

    // --- ローカルストレージから投票データを読み込む ---
    let dailyVotes = { count: 0, date: new Date().toLocaleDateString() };
    const savedVotes = localStorage.getItem('dailyVoteData');
    if (savedVotes) {
        const parsedData = JSON.parse(savedVotes);
        if (parsedData.date === dailyVotes.date) {
            dailyVotes = parsedData;
        } else {
            localStorage.setItem('dailyVoteData', JSON.stringify(dailyVotes));
        }
    }

    // --- UIを更新する関数 ---
    function updateUI() {
        const votesLeft = MAX_VOTES_PER_DAY - dailyVotes.count;
        votesRemainingElement.textContent = votesLeft;

        if (votesLeft <= 0) {
            voteButtons.forEach(button => {
                button.disabled = true;
                button.textContent = '本日の上限です';
            });
        }
    }

    const voteLimiter = document.getElementById('vote-limiter');

// 画面幅をチェックするメディアクエリ
const mediaQuery = window.matchMedia('(max-width: 768px)');

function handleScroll() {
    // ページ全体の高さ (より正確な方法に変更)
    const scrollHeight = document.documentElement.scrollHeight;
    // 表示領域の高さ
    const clientHeight = document.documentElement.clientHeight;
    // 現在のスクロール位置
    const scrollY = window.scrollY;

    // 一番下までスクロールしたかをチェック (20pxの遊びを持たせる)
    const isAtBottom = scrollY + clientHeight >= scrollHeight - 20;

    if (isAtBottom) {
        voteLimiter.classList.add('is-hidden');
    } else {
        voteLimiter.classList.remove('is-hidden');
    }
}

// 画面幅に応じてイベントリスナーを追加/削除する関数
function setupScrollListener(event) {
    if (event.matches) {
        // 画面が狭い場合 (スマホ) はスクロール監視を開始
        window.addEventListener('scroll', handleScroll);
    } else {
        // 画面が広い場合 (PC) はスクロール監視を解除し、常に表示
        window.removeEventListener('scroll', handleScroll);
        voteLimiter.classList.remove('is-hidden');
    }
}

// 初回読み込み時にチェック
setupScrollListener(mediaQuery);

// 画面幅が変わったときにもチェック
mediaQuery.addEventListener('change', setupScrollListener);

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // --- 投票処理の関数 ---
    function handleVote(button, weaponId) {
        if (dailyVotes.count >= MAX_VOTES_PER_DAY) {
            alert('本日の投票回数の上限に達しました。');
            return;
        }

        const originalText = '投票する'; // 元のテキストを定義
        button.disabled = true;
        // button.textContent = '投票中...'; // 瞬時に処理が終わるため不要に

        fetch('/vote', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // ここでトークンをヘッダーに含める
            },
            body: JSON.stringify({ weapon_id: parseInt(weaponId, 10) }),
        })
        .then(response => { // thenの中身を少し修正
            if (!response.ok) {
                // レートリミット超過(429)などのエラーをここで捕捉
                alert('リクエストが多すぎます。少し時間を置いてから再試行してください。');
                throw new Error('Too Many Requests');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const voteCountElement = document.getElementById(`vote-count-${weaponId}`);
                if (voteCountElement) {
                    voteCountElement.textContent = `${data.new_vote_count} 票`;
                }
                dailyVotes.count++;
                localStorage.setItem('dailyVoteData', JSON.stringify(dailyVotes));
                updateUI();

                // ▼▼▼ 変更点 ▼▼▼
                // 投票完了後、すぐにボタンを再度有効化する
                if (dailyVotes.count < MAX_VOTES_PER_DAY) {
                    button.disabled = false;
                }
                // ▲▲▲ 変更点 ▲▲▲

            } else {
                alert('投票に失敗しました。');
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました。');
            button.disabled = false;
        });
    }

    // --- 初期化処理 ---
    voteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const weaponId = button.dataset.id;
            handleVote(button, weaponId);
        });
    });
    updateUI();
});