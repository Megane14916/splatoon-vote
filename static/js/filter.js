document.addEventListener('DOMContentLoaded', () => {
    // --- DOM要素の取得 ---
    const typeFilter = document.getElementById('type-filter');
    const subFilter = document.getElementById('sub-filter');
    const specialFilter = document.getElementById('special-filter');
    const sortOrder = document.getElementById('sort-order'); // ▼▼▼ 追加 ▼▼▼

    function handleFilterChange() {
        // --- 現在の選択値を取得 ---
        const selectedType = typeFilter.value;
        const selectedSub = subFilter.value;
        const selectedSpecial = specialFilter.value;
        const selectedSort = sortOrder.value; // ▼▼▼ 追加 ▼▼▼

        // --- URLのクエリパラメータを構築 ---
        const params = new URLSearchParams();
        params.append('page', '1'); // フィルターやソート変更時は1ページ目に戻す
        
        if (selectedType !== 'all') {
            params.append('type', selectedType);
        }
        if (selectedSub !== 'all') {
            params.append('sub', selectedSub);
        }
        if (selectedSpecial !== 'all') {
            params.append('special', selectedSpecial);
        }
        if (selectedSort !== 'default') { // ▼▼▼ 追加 ▼▼▼
            params.append('sort', selectedSort);
        }

        // --- ページをリロード ---
        window.location.href = `/?${params.toString()}`;
    }

    // --- イベントリスナーを設定 ---
    typeFilter.addEventListener('change', handleFilterChange);
    subFilter.addEventListener('change', handleFilterChange);
    specialFilter.addEventListener('change', handleFilterChange);
    sortOrder.addEventListener('change', handleFilterChange); // ▼▼▼ 追加 ▼▼▼
});