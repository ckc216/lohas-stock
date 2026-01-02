# 📈 股票智慧分析儀 (Stock Intelligence)

這是一個使用 Streamlit 打造的互動式股票分析應用程式，專為台灣股市設計，提供「樂活五線譜」與「樂活通道」兩種視覺化分析工具，以洞察股價趨勢與波動。

## ✨ 主要功能

*   **樂活五線譜 (Lohas 5-Lines)**: 透過線性迴歸計算股價的長期趨勢線，並繪製出 ±1 和 ±2 個標準差的區間帶，以評估股價的相對位置。
*   **樂活通道 (Lohas Channel)**: 計算股價的 100 日移動平均線 (MA) 及上下兩個標準差的通道，用來觀察股價的中期波動範圍。
*   **簡易搜尋**: 可透過股票中文名稱或代碼快速搜尋。
*   **即時資訊**: 顯示股票的最新股價、代號及資料更新日期。
*   **互動式圖表**: 使用 Plotly 提供可縮放、移動和懸停顯示詳細資訊的互動式圖表。
*   **資料來源**: 所有股票資料均透過 [FinMind API](https://finmind.github.io/FinMind/) 即時取得。
*   **客製化介面**: 採用類 Apple 的簡潔白色 UI 設計，提供優雅的使用體驗。

## 🚀 如何在本地端運行

1.  安裝所需的 Python 套件：

    ```bash
    pip install -r requirements.txt
    ```

2.  執行 Streamlit 應用程式：

    ```bash
    streamlit run streamlit_app.py
    ```

