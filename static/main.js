const outputElement = document.getElementById("output");

// Utility function to send requests
async function sendRequest(url, method = "GET", body = null) {
    try {
        const options = { method, headers: { "Content-Type": "application/json" } };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const result = await response.json();
            outputElement.textContent = JSON.stringify(result, null, 2);
        } else if (contentType && contentType.includes("text/html")) {
            const result = await response.text();
            outputElement.innerHTML = result; // HTML을 직접 삽입
        } else {
            throw new Error("Unsupported response type");
        }
    } catch (error) {
        outputElement.textContent = `Error: ${error.message}`;
    }
}

// Event handlers for each section
document.body.addEventListener("click", (event) => {
    const action = event.target.dataset.action;
    console.log("Action:", action); // Add this line to debug
    if (!action) return;

    let url = "";
    let body = null;
    
    switch (action) {
        ////////////////////////////  params.html  ////////////////////////////
        case "set-indicator-params":
            const indicatorExchangeName = document.getElementById("indicator-exchange-name").value.trim();
            const maType = document.getElementById("ma-type").value.trim();
            const srcType = document.getElementById("src-type").value.trim();
            const maLength = parseInt(document.getElementById("ma-length").value);
            const timeFrame = document.getElementById("timeframe").value.trim();
            const turnoverPeriod = parseInt(document.getElementById("turnover-period").value);
            body = { 
                exchange_name: indicatorExchangeName, 
                indicator_params: { 
                    ma_type: maType, 
                    src_type: srcType, 
                    ma_length: maLength,
                    timeframe: timeFrame,
                    turnover_period: turnoverPeriod
                } 
            };
            url = "/set_indicator_params";
            break;

        case "set-signal-params":
            const signalExchangeName = document.getElementById("signal-exchange-name").value.trim();
            const levelList = document.getElementById("level-list").value.trim().split(",").map(Number);
            const closeDeviation = parseFloat(document.getElementById("close-deviation").value);
            const nearGap = parseFloat(document.getElementById("near-gap").value);
            const nearGapType = document.getElementById("near-gap-type").value.trim();
            const turnoverThreshold = parseFloat(document.getElementById("turnover-threshold").value);
            body = { 
                exchange_name: signalExchangeName, 
                signal_params: { 
                    level_list: levelList, 
                    close_deviation: closeDeviation, 
                    near_gap: nearGap, 
                    near_gap_type: nearGapType, 
                    turnover_threshold: turnoverThreshold
                } 
            };
            url = "/set_signal_params";
            break;

        case "set-betting-params":
            const bettingExchangeName = document.getElementById("betting-exchange-name").value.trim();
            const nMax = parseInt(document.getElementById("nmax").value);
            const bettingType = document.getElementById("betting-type").value.trim();
            const balancePerCoin = parseFloat(document.getElementById("balance-per-coin").value);
            const liquidationMdd = parseFloat(document.getElementById("liquidation-mdd").value);
            const leverage = parseInt(document.getElementById("leverage").value);
            const marginMode = document.getElementById("margin-mode").value.trim();
            const safetyMarginPercent = parseFloat(document.getElementById("safety-margin-percent").value);
            body = { 
                exchange_name: bettingExchangeName, 
                betting_params: { 
                    nmax: nMax, 
                    betting_type: bettingType, 
                    balance_per_coin: balancePerCoin, 
                    liquidation_mdd: liquidationMdd, 
                    leverage: leverage, 
                    margin_mode: marginMode, 
                    safety_margin_percent: safetyMarginPercent 
                } 
            };
            url = "/set_betting_params";
            break;

        case "view-params":
            const viewExchangeName = document.getElementById("view-exchange-name").value.trim();
            body = { exchange_name: viewExchangeName };
            url = "/view_params";
            break;


        ////////////////////////////  symbols.html  ////////////////////////////
        case "reload-markets":
            body = { password: document.getElementById("password").value.trim() };
            url = "/reload_markets";
            break;
            
        case "add-multiple-symbols":
        case "remove-multiple-symbols":
        case "remove-multiple-symbols-force":
            const multiSymbolExchangeName = document.getElementById("multi-symbol-exchange-name").value.trim();
            const symbols = document.getElementById("multi-symbols").value.trim().split(",").map(s => s.trim());
            body = { exchange_name: multiSymbolExchangeName, symbols: symbols };
            if (action === "remove-multiple-symbols-force") {
                url = "/remove_symbols_force";
            } else {
                url = `/${action.replace("-multiple-symbols", "_symbols")}`;
            }
            break;

        case "remove-all-symbols":
        case "remove-all-symbols-force":
            const removeAllExchangeName = document.getElementById("multi-symbol-exchange-name").value.trim();
            body = { exchange_name: removeAllExchangeName };
            if (action === "remove-all-symbols") {
                url = "/remove_all_symbols";
            }
            if (action === "remove-all-symbols-force") {
                url = "/remove_all_symbols_force";
            }
            break;

        case "view-symbols":
            const viewSymbolsExchangeName = document.getElementById("view-symbols-exchange-name").value.trim();
            body = { exchange_name: viewSymbolsExchangeName };
            url = "/view_symbols";
            break;
        

        ////////////////////////////  monitoring.html  ////////////////////////////
        case "log-trace":
        case "log-debug":
        case "log-info":
        case "log-success":
        case "log-warning":
        case "log-error":
        case "log-critical":
            body = { log_level: action.replace("log-", "").toUpperCase() };
            url = "/log_level";
            break;

        case "monitoring-params":
            const monitoringParamsExchangeName = document.getElementById("monitoring-exchange-name").value.trim();
            body = { exchange_name: monitoringParamsExchangeName };
            url = "/view_params";
            break;

        case "monitoring-symbols":
            const monitoringSymbolsExchangeName = document.getElementById("monitoring-exchange-name").value.trim();
            body = { exchange_name: monitoringSymbolsExchangeName };
            url = "/view_symbols";
            break;

        case "monitoring-signal-status":
            const signalStatusExchangeName = document.getElementById("monitoring-exchange-name").value.trim();
            body = { exchange_name: signalStatusExchangeName };
            url = "/view_signal_status";
            break;

        case "monitoring-exchange-status":
            const exchangeStatusExchangeName = document.getElementById("monitoring-exchange-name").value.trim();
            body = { exchange_name: exchangeStatusExchangeName };
            url = "/view_exchange_status";
            break;

        case "monitoring-shared-memory":
            body = { password: document.getElementById("password").value.trim() };
            url = "/view_shared_memory";
            break;

        ////////////////////////////  admin.html  ////////////////////////////
        case "on-whitelist":
            url = "/use_whitelist/1";
            break;
        case "off-whitelist":
            url = "/use_whitelist/0";
            break;
        case "reset-exchange-manager":
            const resetExchangeManagerExchangeName = document.getElementById("core-control-exchange-name").value.trim();
            body = { exchange_name: resetExchangeManagerExchangeName };
            url = "/reset_exchange_manager";
            break;

        case "view-exchange-manager":
            const viewExchangeManagerExchangeName = document.getElementById("core-control-exchange-name").value.trim();
            body = { exchange_name: viewExchangeManagerExchangeName };
            url = "/view_exchange_status";
            break;

        case "tv-hatiko-clean-signal-status":
            const tvHatikoCleanExchangeName = document.getElementById("tv-hatiko-exchange-name").value.trim();
            const tvHatikoSymbols = document.getElementById("tv-hatiko-symbols").value.trim().split(",").map(s => s.trim());
            body = { exchange_name: tvHatikoCleanExchangeName, symbols: tvHatikoSymbols };
            url = "/tv_hatiko/clean_signal_status";
            break;

        // "tv-hatiko-view-signal-status" 는 plugins.html 영역에서 처리

        ////////////////////////////  plugins.html  ////////////////////////////
        case "tv-hatiko-set-params":
            const useKillConfirm = document.getElementById("use-kill-confirm").value == "True";
            const killMinute = parseInt(document.getElementById("kill-minute").value);
            body = { use_kill_confirm: useKillConfirm, kill_minute: killMinute}
            url = "/tv_hatiko/set_params";
            break;

        case "tv-hatiko-view-params":
            body = { password: document.getElementById("password").value.trim() };
            url = "/tv_hatiko/view_params";
            break;
        
        case "tv-hatiko-view-signal-status":
            body = { password: document.getElementById("password").value.trim() };
            url = "/tv_hatiko/view_signal_status";
            break;

            
        case "symbol-db-symbol-date-map-set-symbol-date":
            const symbolDbSetSymbolDateExchange = document.getElementById("symbol-db-symbol-date-map-exchange-name").value.trim();
            const symbolDbSetSymbolDateDate = document.getElementById("symbol-db-symbol-date-map-date").value.trim();
            const symbolDbSetSymbolDateMultiSymbols = document.getElementById("symbol-db-symbol-date-map-multi-symbols").value.trim().split(",").map(s => s.trim());
            body = { exchange_name: symbolDbSetSymbolDateExchange, date: symbolDbSetSymbolDateDate, symbols: symbolDbSetSymbolDateMultiSymbols };
            url = "/symbol_db/set_symbol_date";
            break;
        
        case "symbol-db-symbol-date-map-remove-from-pending-map":
            const symbolDbRemovePendingMapExchangeName = document.getElementById("symbol-db-symbol-date-map-exchange-name").value.trim();
            const symbolDbRemovePendingMapMultiSymbols = document.getElementById("symbol-db-symbol-date-map-multi-symbols").value.trim().split(",").map(s => s.trim());
            body = { exchange_name: symbolDbRemovePendingMapExchangeName, symbols: symbolDbRemovePendingMapMultiSymbols };
            url = "/symbol_db/remove_symbol_date_pending_map";
            break;

        case "symbol-db-symbol-date-map-view-pending-map":
            const symbolDbViewPendingMapExchangeName = document.getElementById("symbol-db-symbol-date-map-exchange-name").value.trim();
            body = { exchange_name: symbolDbViewPendingMapExchangeName};
            url = "/symbol_db/view_symobl_date_pending_map";
            break;

        case "symbol-db-view-symbol-db-sort-by-turnover":
        case "symbol-db-view-symbol-db-sort-by-date":
            const symbolDbViewExchangeName = document.getElementById("symbol-db-view-symbol-db-exchange-name").value.trim();
            const symbolDbViewExchangesToExcludeCheckBoxes = document.querySelectorAll('input[name="symbol-db-view-symbol-db-exchanges-to-exclude"]:checked');
            const symbolDbViewExchangesToExclude = Array.from(symbolDbViewExchangesToExcludeCheckBoxes).map(checkbox => checkbox.value);
            const symbolDbViewSince = document.getElementById("symbol-db-view-symbol-db-since").value.trim();
            const symbolDbViewMarketType = document.getElementById("symbol-db-view-symbol-db-market-type").value.trim();
            body = { 
                exchange_name: symbolDbViewExchangeName, 
                exchanges_to_exclude: symbolDbViewExchangesToExclude,
                sort_by: action.replace("symbol-db-view-symbol-db-sort-by-", ""), 
                market_type: symbolDbViewMarketType,
                since: symbolDbViewSince
            };
            url = "/symbol_db/view_symbol_db";
            break;

        case "kc-trend-view-status":
            body = { password: document.getElementById("password").value.trim() };
            url = "/kc_trend/view_status";
            break;

        ////////////////////////////  default  ////////////////////////////
        default:
            alert("Unknown action!");
            return;
    }

    // Add password to the body
    if (body) {
        const password = document.getElementById("password").value.trim();
        body.password = password;
    } 

    sendRequest(url, body ? "POST" : "GET", body);
});