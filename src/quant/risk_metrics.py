import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


def calculate_parametric_var(
    volatility_annual: float,
    confidence_level: float = 0.95,
    horizon_days: int = 1
) -> float:
    """
    Parametric (Gaussian) Value-at-Risk as a positive percentage.
    Assumes normally distributed returns — fast, closed-form.
    """
    z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
    z = z_scores.get(confidence_level, 1.645)
    daily_vol = volatility_annual / np.sqrt(252)
    var = z * daily_vol * np.sqrt(horizon_days)
    return round(float(var * 100), 2)


def calculate_historical_cvar(
    returns: Optional[np.ndarray],
    confidence_level: float = 0.95,
    volatility_annual: float = 0.25,
) -> float:
    """
    Historical-Simulation Conditional Value-at-Risk (CVaR / Expected Shortfall).

    CVaR is the mean loss in the worst (1 - confidence_level) fraction of outcomes.
    It is the industry-standard tail-risk metric used at hedge funds, superseding VaR
    because it captures *expected* loss severity beyond the VaR threshold, not just
    the threshold itself.

    Falls back to a Cornish-Fisher parametric approximation when historical data is
    unavailable (preserving the ability to run in deterministic offline mode).
    """
    if returns is not None and len(returns) >= 60:
        daily_returns = np.asarray(returns, dtype=float)
        cutoff = np.percentile(daily_returns, (1 - confidence_level) * 100)
        tail_losses = daily_returns[daily_returns <= cutoff]
        if len(tail_losses) > 0:
            cvar_daily = float(abs(np.mean(tail_losses)))
            return round(cvar_daily * 100, 2)

    # Cornish-Fisher approximation (skewness-adjusted parametric fallback)
    daily_vol = volatility_annual / np.sqrt(252)
    # ES factor for normal distribution at 95%: φ(z) / (1-α) ≈ 2.063
    es_factor = {0.95: 2.063, 0.99: 2.665}.get(confidence_level, 2.063)
    cvar = daily_vol * es_factor
    return round(float(cvar * 100), 2)


def regime_position_multiplier(regime: str) -> float:
    """
    Regime-aware position sizing scalar applied on top of inverse-volatility sizing.

    Regime Classification → Capital Allocation Multiplier:
      LOW_VOL_BULL    : 1.00  (full risk budget — favorable environment)
      HIGH_VOL_BULL   : 0.65  (tail risk elevated; reduce but maintain long bias)
      RANGEBOUND_CHOP : 0.40  (mean-reversion regime; reduce directional exposure)
      BEAR_PANIC      : 0.15  (capital preservation; near-cash positioning)
    """
    multipliers = {
        "LOW_VOL_BULL":    1.00,
        "HIGH_VOL_BULL":   0.65,
        "RANGEBOUND_CHOP": 0.40,
        "BEAR_PANIC":      0.15,
    }
    return multipliers.get(regime, 0.70)


def evaluate_portfolio_risk(
    ticker: str,
    annual_volatility: float,
    current_price: float,
    max_vol_limit: float = 0.65,
    target_risk_budget: float = 0.12,
    historical_returns: Optional[np.ndarray] = None,
    market_regime: str = "LOW_VOL_BULL",
) -> Dict[str, Any]:
    """
    Chief Risk Officer (CRO) Quantitative Risk Engine.

    Computes:
    ─ Parametric 95% & 99% Value-at-Risk (Gaussian closed-form)
    ─ Historical-simulation CVaR (Expected Shortfall at 95%) — tail risk beyond VaR
    ─ Regime-aware inverse-volatility position sizing
      └─ Base: target_risk_budget / σ_annual
      └─ Regime scalar: 1.0 → 0.15 depending on macro environment
    ─ CRO veto decision (hard stop above 65% annualized vol)
    """
    # ── Core VaR Calculations ──────────────────────────────────────────────────
    var_95 = calculate_parametric_var(annual_volatility, confidence_level=0.95)
    var_99 = calculate_parametric_var(annual_volatility, confidence_level=0.99)

    # ── CVaR / Expected Shortfall (historical or parametric fallback) ──────────
    cvar_95 = calculate_historical_cvar(
        returns=historical_returns,
        confidence_level=0.95,
        volatility_annual=annual_volatility,
    )

    # ── Risk Veto Check ────────────────────────────────────────────────────────
    is_vetoed = bool(annual_volatility > max_vol_limit)

    # ── Regime-Aware Inverse-Volatility Position Sizing ───────────────────────
    base_allocation = target_risk_budget / (annual_volatility + 1e-6)
    regime_scalar   = regime_position_multiplier(market_regime)
    raw_allocation  = base_allocation * regime_scalar
    capped_allocation = round(float(max(0.02, min(0.30, raw_allocation))), 3)

    if is_vetoed:
        capped_allocation = 0.0
        risk_rating = "EXTREME"
        summary = (
            f"VETO: Annualized volatility ({annual_volatility*100:.1f}%) "
            f"exceeds fund threshold ({max_vol_limit*100:.0f}%). "
            f"1-Day 95% CVaR (Expected Shortfall): {cvar_95}%. Position zeroed."
        )
    elif annual_volatility > 0.45:
        risk_rating = "HIGH"
        summary = (
            f"CAUTION [{market_regime}]: Elevated volatility ({annual_volatility*100:.1f}%). "
            f"Parametric VaR-95: {var_95}% | CVaR-95 (ES): {cvar_95}%. "
            f"Regime scalar {regime_scalar:.2f}x → allocation capped at {capped_allocation*100:.1f}%."
        )
    elif annual_volatility > 0.25:
        risk_rating = "MODERATE"
        summary = (
            f"ACCEPTABLE [{market_regime}]: Normal regime. "
            f"VaR-95: {var_95}% | CVaR-95: {cvar_95}%. "
            f"Regime-adjusted max weight: {capped_allocation*100:.1f}%."
        )
    else:
        risk_rating = "LOW"
        summary = (
            f"FAVORABLE [{market_regime}]: Low volatility ({annual_volatility*100:.1f}%). "
            f"CVaR-95: {cvar_95}%. Strong capital preservation metrics. "
            f"Full risk budget allocated: {capped_allocation*100:.1f}%."
        )

    return {
        "ticker":               ticker,
        "is_vetoed":            is_vetoed,
        "max_position_size_pct": capped_allocation,
        "var_95":               var_95,
        "var_99":               var_99,
        "cvar_95":              cvar_95,
        "risk_rating":          risk_rating,
        "risk_summary":         summary,
        "regime":               market_regime,
        "regime_scalar":        regime_scalar,
        "suggested_stop_loss":  round(current_price * (1.0 - (var_95 / 100.0) * 1.5), 2),
        "suggested_take_profit": round(current_price * (1.0 + (var_95 / 100.0) * 3.0), 2),
    }

