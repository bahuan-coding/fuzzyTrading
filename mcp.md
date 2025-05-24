{
  "version": "1.2",
  "neutrality_implementation": {
    "neutrality_type": "Dollar Neutral (Buy Notional = Sell Notional)",
    "pairing_method": {
      "description": "Manual pairing of buy/sell signals to equal monetary value",
      "step_by_step": [
        {
          "step": "Calculate Signal Scores",
          "details": "Compute FuzzyFajuto scores for all stocks as in original logic"
        },
        {
          "step": "Create Buy/Sell Lists",
          "details": {
            "buy_candidates": "All stocks with score ≥1.5, sorted by PRICE (lowest first)",
            "sell_candidates": "All stocks with score ≤-1.5, sorted by PRICE (lowest first)",
            "sorting_logic": "Prioritize cheaper stocks to maximize position count"
          }
        },
        {
          "step": "Pair Construction",
          "details": {
            "method": "Sequential Pairing",
            "process": [
              "1. Take top stock from Buy List (e.g. Stock A @ R$10)",
              "2. Find cheapest Sell List stock with similar value (e.g. Stock B @ R$9.80)",
              "3. Adjust quantities to equalize notional:",
              "   - Buy 100 shares of A (R$1,000)",
              "   - Sell 102 shares of B (R$999.60 ≈ R$1,000)",
              "4. Remove paired stocks from lists",
              "5. Repeat until no valid pairs remain"
            ],
            "tolerance": "Allow 2% notional mismatch for practicality"
          }
        },
        {
          "step": "Position Sizing",
          "details": {
            "base_size": "Fixed amount per pair (e.g. R$2,000 total: R$1k long + R$1k short)",
            "excel_formula": "=ROUND(base_size/price, 0)",
            "constraints": [
              "Minimum quantity: 100 shares per leg",
              "Maximum single position: 5% of portfolio"
            ]
          }
        }
      ]
    },
    "rebalancing": {
      "frequency": "Daily at market open",
      "process": [
        "1. Close all existing positions",
        "2. Recalculate scores for new day",
        "3. Build new neutral pairs"
      ]
    },
    "excel_tools": {
      "required_columns": [
        "Stock",
        "Price",
        "Score",
        "Signal (Buy/Sell)",
        "Target Quantity",
        "Pair ID",
        "Pair Notional Difference (%)"
      ],
      "formula_examples": {
        "signal": "=IF(Score>=1.5,\"Buy\",IF(Score<=-1.5,\"Sell\",\"\"))",
        "pair_matching": "Use VLOOKUP to find nearest-price opposite signal",
        "notional_check": "=ABS((Buy_Value - Sell_Value)/AVERAGE(Buy_Value,Sell_Value))"
      }
    },
    "neutrality_checks": {
      "pre_trade": "Sum all Buy Values ≈ Sum all Sell Values (within 2%)",
      "post_trade": "Verify actual fills maintained neutrality",
      "adjustment_rules": [
        "If Buy notional > Sell: Reduce quantities of most expensive buys",
        "If Sell notional > Buy: Reduce quantities of most expensive shorts"
      ]
    }
  },
  "example_pair": {
    "buy_leg": {
      "stock": "PETR4",
      "price": 32.50,
      "quantity": 307,
      "notional": 9,977.50
    },
    "sell_leg": {
      "stock": "VALE3",
      "price": 65.20,
      "quantity": 153,
      "notional": 9,975.60
    },
    "imbalance": 0.02%
  }
}
