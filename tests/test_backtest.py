            15,
        ]
    )

    result = build_metrics(
        equity,
        trades,
        benchmark_return=8.0,
    )

    required = {
        "WinRate",
        "AverageGain",
        "AverageLoss",
        "ProfitFactor",
        "Expectancy",
        "TotalReturn",
        "CAGR",
        "SharpeRatio",
        "SortinoRatio",
        "MaxDrawdown",
        "BenchmarkReturn",
        "Alpha",
    }

    assert required.issubset(
        result.keys()
    )


def test_alpha_calculation():
    equity = pd.Series(
        [
            100,
            120,
        ]
    )

    trades = pd.Series([20])

    metrics = build_metrics(
        equity,
        trades,
        benchmark_return=10,
    )
