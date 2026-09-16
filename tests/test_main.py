from unittest.mock import Mock, call

import scanner.scanner as scanner_module


def make_passed_outcome(ticker="AAPL", score=85, risk_reward=2.0):
    """Return the minimum valid Passed outcome required by main()."""
    return {
        "Ticker": ticker,
        "Status": "Passed",
        "Reason": "PASS",
        "Metrics": {
            "Price": 150.0,
            "MA20": 145.0,
            "MA50": 140.0,
            "MA200": 130.0,
            "RSI": 60.0,
            "VolumeRatio": 1.2,
            "RelativeStrength": 5.0,
            "RSComposite": 4.0,
        },
        "FilterEvaluations": [
            {
                "Passed": True,
                "Reason": "PASS",
            }
        ],
        "Result": {
            "Ticker": ticker,
            "TradePlan": "✅ ACTIONABLE",
            "Signal": "STRONG BUY",
            "Score": score,
            "MarketRegime": "BULL",
            "RegimeScore": 15,
            "RiskReward": risk_reward,
            "RS21": 2.0,
            "RS63": 5.0,
            "RS126": 6.0,
            "RS252": 8.0,
            "RSComposite": 4.0,
            "VolumeSource": "Latest completed session",
            "VolumeRatio": 1.2,
        },
    }


def make_filtered_outcome(ticker="MSFT"):
    """Return a Filtered outcome with multiple failed conditions."""
    return {
        "Ticker": ticker,
        "Status": "Filtered",
        "Reason": "VolumeRatio below 0.8",
        "Metrics": {
            "Price": 300.0,
            "MA20": 295.0,
            "MA50": 290.0,
            "MA200": 275.0,
            "RSI": 55.0,
            "VolumeRatio": 0.6,
            "RelativeStrength": 3.0,
            "RSComposite": 2.0,
        },
        "FilterEvaluations": [
            {
                "Passed": True,
                "Reason": "PASS",
            },
            {
                "Passed": False,
                "Reason": "VolumeRatio below 0.8",
            },
        ],
        "Result": None,
    }


def make_data_failure_outcome(ticker="NVDA"):
    """Return a Data Failure outcome."""
    return {
        "Ticker": ticker,
        "Status": "Data Failure",
        "Reason": "Download returned no usable data",
        "Metrics": None,
        "FilterEvaluations": [],
        "Result": None,
    }


def test_main_exits_early_for_bear_market(monkeypatch):
    """BEAR regime must send an alert and stop before stock processing."""
    tickers = ["AAPL", "MSFT"]

    monkeypatch.setattr(scanner_module, "USE_SP500", True)
    monkeypatch.setattr(
        scanner_module,
        "get_sp500_tickers",
        Mock(return_value=tickers),
    )
    monkeypatch.setattr(
        scanner_module,
        "get_market_context",
        Mock(
            return_value={
                "spy_price": 400.0,
                "spy_ma200": 450.0,
                "spy_returns": {
                    21: -2.0,
                    63: -5.0,
                    126: -8.0,
                    252: -10.0,
                },
                "market_bull": False,
            }
        ),
    )
    monkeypatch.setattr(
        scanner_module,
        "classify_market_regime",
        Mock(return_value="BEAR"),
    )

    mock_bear_email = Mock()
    mock_analyse_stock = Mock()
    mock_export_excel = Mock()
    mock_send_email = Mock()

    monkeypatch.setattr(
        scanner_module,
        "send_bear_market_email",
        mock_bear_email,
    )
    monkeypatch.setattr(
        scanner_module,
        "analyse_stock",
        mock_analyse_stock,
    )
    monkeypatch.setattr(
        scanner_module,
        "export_excel",
        mock_export_excel,
    )
    monkeypatch.setattr(
        scanner_module,
        "send_email",
        mock_send_email,
    )

    scanner_module.main()

    mock_bear_email.assert_called_once_with(
        400.0,
        450.0,
        "BEAR",
    )

    mock_analyse_stock.assert_not_called()
    mock_export_excel.assert_not_called()
    mock_send_email.assert_not_called()


def test_main_runs_complete_bull_market_scan(monkeypatch):
    """BULL regime must process Passed and Filtered outcomes."""
    tickers = ["AAPL", "MSFT"]

    spy_returns = {
        21: 1.0,
        63: 3.0,
        126: 5.0,
        252: 8.0,
    }

    monkeypatch.setattr(scanner_module, "USE_SP500", True)
    monkeypatch.setattr(
        scanner_module,
        "get_sp500_tickers",
        Mock(return_value=tickers),
    )
    monkeypatch.setattr(
        scanner_module,
        "get_market_context",
        Mock(
            return_value={
                "spy_price": 500.0,
                "spy_ma200": 450.0,
                "spy_returns": spy_returns,
                "market_bull": True,
            }
        ),
    )
    monkeypatch.setattr(
        scanner_module,
        "classify_market_regime",
        Mock(return_value="BULL"),
    )

    mock_analyse_stock = Mock(
        side_effect=[
            make_passed_outcome("AAPL"),
            make_filtered_outcome("MSFT"),
        ]
    )
    monkeypatch.setattr(
        scanner_module,
        "analyse_stock",
        mock_analyse_stock,
    )

    mock_export_excel = Mock(return_value="bull_report.xlsx")
    monkeypatch.setattr(
        scanner_module,
        "export_excel",
        mock_export_excel,
    )

    mock_build_email_body = Mock(return_value="Bull diagnostic report")
    monkeypatch.setattr(
        scanner_module,
        "build_email_body",
        mock_build_email_body,
    )

    mock_send_email = Mock()
    monkeypatch.setattr(
        scanner_module,
        "send_email",
        mock_send_email,
    )

    monkeypatch.setattr(scanner_module.time, "sleep", Mock())

    scanner_module.main()

    assert mock_analyse_stock.call_args_list == [
        call("AAPL", True, spy_returns, "BULL"),
        call("MSFT", True, spy_returns, "BULL"),
    ]

    mock_export_excel.assert_called_once()

    exported_top20 = mock_export_excel.call_args.args[0]

    assert len(exported_top20) == 1
    assert exported_top20.iloc[0]["Rank"] == 1
    assert exported_top20.iloc[0]["Ticker"] == "AAPL"
    assert exported_top20.iloc[0]["MarketRegime"] == "BULL"
    assert exported_top20.iloc[0]["RegimeScore"] == 15

    mock_build_email_body.assert_called_once()

    email_top20 = mock_build_email_body.call_args.args[0]
    email_status_counts = mock_build_email_body.call_args.args[2]
    email_rejection_counts = mock_build_email_body.call_args.args[3]
    email_breadth_counts = mock_build_email_body.call_args.args[4]

    assert len(email_top20) == 1
    assert email_status_counts["Passed"] == 1
    assert email_status_counts["Filtered"] == 1
    assert email_rejection_counts["VolumeRatio below 0.8"] == 1
    assert email_breadth_counts["Indicator-ready stocks"] == 2

    mock_send_email.assert_called_once_with(
        f"📈 US Scanner {scanner_module.VERSION} Daily Diagnostic Report",
        "Bull diagnostic report",
        "bull_report.xlsx",
    )


def test_main_runs_neutral_market_with_empty_results(monkeypatch):
    """NEUTRAL regime must continue scanning and generate an empty report."""
    tickers = ["NVDA"]

    spy_returns = {
        21: 0.0,
        63: 0.5,
        126: 1.0,
        252: 2.0,
    }

    monkeypatch.setattr(scanner_module, "USE_SP500", True)
    monkeypatch.setattr(
        scanner_module,
        "get_sp500_tickers",
        Mock(return_value=tickers),
    )
    monkeypatch.setattr(
        scanner_module,
        "get_market_context",
        Mock(
            return_value={
                "spy_price": 501.0,
                "spy_ma200": 500.0,
                "spy_returns": spy_returns,
                "market_bull": True,
            }
        ),
    )
    monkeypatch.setattr(
        scanner_module,
        "classify_market_regime",
        Mock(return_value="NEUTRAL"),
    )
    monkeypatch.setattr(
        scanner_module,
        "analyse_stock",
        Mock(return_value=make_data_failure_outcome("NVDA")),
    )

    mock_export_excel = Mock(return_value="neutral_report.xlsx")
    mock_build_email_body = Mock(return_value="Neutral diagnostic report")
    mock_send_email = Mock()
    mock_bear_email = Mock()

    monkeypatch.setattr(
        scanner_module,
        "export_excel",
        mock_export_excel,
    )
    monkeypatch.setattr(
        scanner_module,
        "build_email_body",
        mock_build_email_body,
    )
    monkeypatch.setattr(
        scanner_module,
        "send_email",
        mock_send_email,
    )
    monkeypatch.setattr(
        scanner_module,
        "send_bear_market_email",
        mock_bear_email,
    )
    monkeypatch.setattr(scanner_module.time, "sleep", Mock())

    scanner_module.main()

    mock_bear
