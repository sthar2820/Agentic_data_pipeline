import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_numeric_dtype,
    is_string_dtype,
    is_categorical_dtype,
)

from orchestrator.types import DataQuality, DataQualityReport
from orchestrator.serialize import save_json


_DEFAULTS: Dict[str, Any] = {
    "dataset_name": "dataset",
    "artifacts_dir": "data/artifacts",
    "outlier_method": "row",     # 'row' or 'cell'
    "sample_size": 500,
    "thresholds": {
        "missing_drop": 0.70,    # >70% missing → suggest drop
        "missing_high": 0.30,    # 30–70%
        "missing_medium": 0.10,  # 10–30%
        "cardinality_low_ratio": 0.05,
        "cardinality_high_ratio": 0.95,
    },
    "modules": {
        "patterns": True,
        "consistency": True,
        "skewness": True
    }
}


class InspectorAgent:
    """
    Enhanced Data Inspector Agent - comprehensive data quality profiling with
    agentic outputs (human-readable recommendations + machine-readable actions).
    """

    def __init__(self, config: Dict[str, Any] = None):
        cfg = config or {}
        # Shallow merge of top-level + nested thresholds/modules
        thresholds = {**_DEFAULTS["thresholds"], **cfg.get("thresholds", {})}
        modules = {**_DEFAULTS["modules"], **cfg.get("modules", {})}
        self.config = {**_DEFAULTS, **cfg, "thresholds": thresholds, "modules": modules}

        self.logger = logging.getLogger(self.__class__.__name__)
        self.dataset_name = self.config["dataset_name"]
        self.artifacts_dir = Path(self.config["artifacts_dir"])
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.outlier_method = self.config["outlier_method"]

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze_data(self, data: pd.DataFrame) -> DataQualityReport:
        self.logger.info(
            f"Inspector: analyzing {data.shape[0]} rows × {data.shape[1]} columns..."
        )

        # Core analysis
        missing_values = self._analyze_missing_values(data)
        data_types = self._analyze_data_types(data)
        duplicate_count = self._count_duplicates(data)
        outlier_count, outlier_details = self._detect_outliers(data)
        column_stats = self._calculate_column_statistics(data)

        # Enhanced analysis
        cardinality = self._analyze_cardinality(data)
        skewness = self._analyze_skewness(data) if self.config["modules"]["skewness"] else {}
        patterns = self._analyze_patterns(data) if self.config["modules"]["patterns"] else {}
        consistency = self._check_consistency(data) if self.config["modules"]["consistency"] else {}
        quality_scores = self._calculate_column_quality_scores(
            data, missing_values, cardinality, consistency
        )

        # Enrich column stats
        for col in column_stats:
            if col in cardinality:
                column_stats[col]["cardinality"] = cardinality[col]
            if col in skewness:
                column_stats[col]["skewness"] = skewness[col]
            if col in patterns:
                column_stats[col]["patterns"] = patterns[col]
            if col in quality_scores:
                column_stats[col]["quality_score"] = quality_scores[col]
            if col in outlier_details:
                column_stats[col]["outliers"] = outlier_details[col]

        # Recommendations + actions
        recommendations = self._generate_recommendations(
            data, missing_values, duplicate_count, outlier_count, data_types,
            cardinality, consistency, quality_scores, patterns
        )
        proposed_actions = self._propose_actions(missing_values, consistency, cardinality)

        # Overall quality
        overall_quality = self._assess_overall_quality(
            missing_values, duplicate_count, outlier_count, quality_scores, len(data)
        )

        report = DataQualityReport(
            overall_quality=overall_quality,
            missing_values=missing_values,
            data_types=data_types,
            duplicate_count=duplicate_count,
            outlier_count=outlier_count,
            column_stats=column_stats,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            cardinality_analysis=cardinality,
            skewness_analysis=skewness,
            pattern_analysis=patterns,
            consistency_issues=consistency,
            column_quality_scores=quality_scores,
            outlier_details=outlier_details,
            proposed_actions=proposed_actions,
        )

        # Persist artifacts
        base = str(self.artifacts_dir / self.dataset_name)
        save_json(report, f"{base}_dq_report.json")
        save_json(proposed_actions, f"{base}_clean_plan.json")

        self.logger.info(f"Inspector complete. Overall quality = {overall_quality.value.upper()}")
        self.logger.info(f"Saved: {base}_dq_report.json and {base}_clean_plan.json")
        return report

    # ------------------------------------------------------------------ #
    # Core analyses
    # ------------------------------------------------------------------ #
    def _analyze_missing_values(self, data: pd.DataFrame) -> Dict[str, float]:
        if len(data) == 0:
            return {c: 0.0 for c in data.columns}
        return ((data.isna().sum() / len(data)) * 100).round(2).to_dict()

    def _analyze_data_types(self, data: pd.DataFrame) -> Dict[str, str]:
        return data.dtypes.astype(str).to_dict()

    def _count_duplicates(self, data: pd.DataFrame) -> int:
        return int(data.duplicated().sum())

    def _detect_outliers(self, data: pd.DataFrame) -> Tuple[int, Dict[str, Dict[str, Any]]]:
        outlier_count = 0
        details: Dict[str, Dict[str, Any]] = {}
        numeric_cols = [c for c in data.columns if is_numeric_dtype(data[c])]

        row_idx: set = set()

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) < 4:
                continue

            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue

            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            mask = (data[col] < lower) | (data[col] > upper)
            col_count = int(mask.sum())

            if self.outlier_method == "cell":
                outlier_count += col_count
            else:
                row_idx.update(data.index[mask].tolist())

            details[col] = {
                "count": col_count,
                "percentage": round((col_count / len(data)) * 100, 2),
                "lower_bound": float(lower),
                "upper_bound": float(upper),
                "Q1": float(Q1),
                "Q3": float(Q3),
                "IQR": float(IQR),
            }

        if self.outlier_method == "row":
            outlier_count = len(row_idx)

        return outlier_count, details

    def _calculate_column_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        stats: Dict[str, Dict[str, Any]] = {}
        n = len(data)

        for col in data.columns:
            col_stats: Dict[str, Any] = {
                "dtype": str(data[col].dtype),
                "non_null_count": int(data[col].count()),
                "null_count": int(data[col].isna().sum()),
                "unique_count": int(data[col].nunique(dropna=True)),
                "missing_pct": round((float(data[col].isna().sum() / max(n, 1)) * 100), 2),
            }

            if is_numeric_dtype(data[col]):
                nn = data[col].dropna()
                if len(nn) > 0:
                    col_stats.update(
                        {
                            "mean": float(nn.mean()),
                            "std": float(nn.std()) if len(nn) > 1 else 0.0,
                            "min": float(nn.min()),
                            "max": float(nn.max()),
                            "median": float(nn.median()),
                            "q25": float(nn.quantile(0.25)),
                            "q75": float(nn.quantile(0.75)),
                        }
                    )
            elif is_string_dtype(data[col]) or is_categorical_dtype(data[col]):
                nn = data[col].dropna().astype(str)
                if len(nn) > 0:
                    vc = nn.value_counts()
                    mode_val = str(vc.index[0]) if len(vc) else None
                    col_stats.update(
                        {
                            "most_common": mode_val,
                            "most_common_freq": int(vc.iloc[0]) if len(vc) else 0,
                            "avg_length": round(float(nn.str.len().mean()), 2),
                            "min_length": int(nn.str.len().min()),
                            "max_length": int(nn.str.len().max()),
                        }
                    )

            stats[col] = col_stats

        return stats

    # ------------------------------------------------------------------ #
    # Enhanced analyses
    # ------------------------------------------------------------------ #
    def _analyze_cardinality(self, data: pd.DataFrame) -> Dict[str, str]:
        out: Dict[str, str] = {}
        n = len(data)
        if n == 0:
            return {c: "constant" for c in data.columns}

        hi = self.config["thresholds"]["cardinality_high_ratio"]
        lo = self.config["thresholds"]["cardinality_low_ratio"]

        for c in data.columns:
            uniq = int(data[c].nunique(dropna=True))
            ratio = uniq / max(n, 1)
            if uniq <= 1:
                out[c] = "constant"
            elif ratio < lo:
                out[c] = "low"
            elif ratio < 0.50:
                out[c] = "medium"
            elif ratio < hi:
                out[c] = "high"
            else:
                out[c] = "unique"
        return out

    def _analyze_skewness(self, data: pd.DataFrame) -> Dict[str, float]:
        sk: Dict[str, float] = {}
        for c in data.columns:
            if is_numeric_dtype(data[c]):
                nn = data[c].dropna()
                if len(nn) > 2 and nn.std() > 0:
                    val = float(nn.skew())
                    if np.isfinite(val):
                        sk[c] = round(val, 3)
        return sk

    def _analyze_patterns(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        patterns: Dict[str, Dict[str, Any]] = {}
        k = int(self.config.get("sample_size", 500))
        for c in data.columns:
            if is_string_dtype(data[c]) or is_categorical_dtype(data[c]):
                ser = data[c].dropna().astype(str)
                if len(ser) == 0:
                    continue
                sample = ser.sample(min(k, len(ser)), random_state=42)
                masks = sample.apply(self._mask)
                vc = masks.value_counts()
                top = vc.head(5).to_dict()
                pct = float((vc.iloc[0] / len(masks)) * 100) if len(vc) else 0.0

                info = {
                    "top_patterns": top,
                    "num_unique_patterns": int(len(vc)),
                    "pattern_consistency_pct": round(pct, 1),
                    "contains_email": bool(sample.str.contains("@", regex=False).any()),
                    "contains_url": bool(sample.str.contains("http", regex=False).any()),
                    "contains_phone": bool(
                        sample.str.match(r".*\d{3}[-.]?\d{3}[-.]?\d{4}.*").any()
                    ),
                    "contains_currency": bool(sample.str.match(r"^\$?[\d,]+\.?\d*$").any()),
                    "is_date_like": self._is_date_like(sample),
                }
                patterns[c] = info
        return patterns

    def _mask(self, s: str) -> str:
        if not isinstance(s, str) or s == "":
            return ""
        out = []
        last = None
        for ch in s:
            if ch.isalpha():
                t = "A"
            elif ch.isdigit():
                t = "#"
            elif ch.isspace():
                t = "W"
            else:
                t = "S"
            if t != last:
                out.append(t)
                last = t
        return "".join(out)

    def _is_date_like(self, series: pd.Series) -> bool:
        sample = series.head(50)
        try:
            parsed = pd.to_datetime(sample, errors="coerce")
            if len(parsed) == 0:
                return False
            return parsed.notna().mean() > 0.7
        except:
            return False

    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        issues: Dict[str, List[str]] = {}
        for c in data.columns:
            if not (is_string_dtype(data[c]) or is_categorical_dtype(data[c])):
                continue
            nn = data[c].dropna().astype(str)
            if len(nn) == 0:
                continue

            sample = nn.sample(min(500, len(nn)), random_state=42)

            probs: List[str] = []

            # numeric-like?
            try:
                num_like = sample.str.replace(",", "", regex=False)\
                                 .str.fullmatch(r"[-+]?\d*\.?\d+").mean()
                if num_like > 0.7:
                    probs.append(f"Numeric-like: {num_like*100:.0f}% numeric strings")
                elif 0.1 < num_like < 0.7:
                    probs.append(f"Mixed: {num_like*100:.0f}% numeric, {(1-num_like)*100:.0f}% text")
            except:
                pass

            # date-like?
            if self._is_date_like(sample):
                probs.append("Date-like: consider datetime parsing")

            # whitespace
            leading = int((sample != sample.str.lstrip()).sum())
            trailing = int((sample != sample.str.rstrip()).sum())
            if leading or trailing:
                probs.append(f"Whitespace: {leading} leading, {trailing} trailing occurrences")

            # case inconsistency
            if sample.str.lower().nunique() < int(sample.nunique() * 0.9):
                probs.append("Case inconsistency: same values with different casing")

            # length variation
            lens = sample.str.len()
            if lens.std() > max(lens.mean(), 1):
                probs.append(f"Length variation: {int(lens.min())}–{int(lens.max())} chars (mean {lens.mean():.1f})")

            if probs:
                issues[c] = probs

        return issues

    def _calculate_column_quality_scores(
        self,
        data: pd.DataFrame,
        missing_values: Dict[str, float],
        cardinality: Dict[str, str],
        consistency_issues: Dict[str, List[str]],
    ) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for c in data.columns:
            score = 1.0

            # completeness (max -0.40)
            miss = missing_values.get(c, 0.0) / 100
            score -= miss * 0.40

            # cardinality (max -0.25)
            card = cardinality.get(c, "medium")
            if card == "constant":
                score -= 0.25
            elif card == "unique" and (is_string_dtype(data[c]) or is_categorical_dtype(data[c])):
                score -= 0.10

            # type consistency (max -0.20)
            if c in consistency_issues:
                score -= min(len(consistency_issues[c]) * 0.07, 0.20)

            # pattern/length consistency for text (max -0.15)
            if is_string_dtype(data[c]) or is_categorical_dtype(data[c]):
                nn = data[c].dropna().astype(str)
                if len(nn) > 1:
                    uniq_ratio = nn.nunique(dropna=True) / len(nn)
                    if uniq_ratio < 0.01:
                        score -= 0.10
                    lens = nn.str.len()
                    if lens.std() > max(lens.mean(), 1):
                        score -= 0.05

            scores[c] = max(0.0, min(1.0, round(score, 3)))
        return scores

    # ------------------------------------------------------------------ #
    # Recommendations & actions
    # ------------------------------------------------------------------ #
    def _generate_recommendations(
        self,
        data: pd.DataFrame,
        missing_values: Dict[str, float],
        duplicate_count: int,
        outlier_count: int,
        data_types: Dict[str, str],
        cardinality: Dict[str, str],
        consistency_issues: Dict[str, List[str]],
        quality_scores: Dict[str, float],
        patterns: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        th = self.config["thresholds"]
        recs: List[str] = []

        constant_cols = [c for c, v in cardinality.items() if v == "constant"]
        if constant_cols:
            recs.append(
                f"CRITICAL: Drop constant columns ({len(constant_cols)}): "
                + ", ".join(constant_cols[:3]) + (" ..." if len(constant_cols) > 3 else "")
            )

        critical_missing = [c for c, pct in missing_values.items() if pct > th["missing_drop"] * 100]
        if critical_missing:
            recs.append(
                f"CRITICAL: >70% missing in {len(critical_missing)} column(s): "
                + ", ".join(critical_missing[:3]) + (" ..." if len(critical_missing) > 3 else "")
            )

        if duplicate_count > 0:
            dup_pct = duplicate_count / max(len(data), 1) * 100
            recs.append(f"HIGH: Remove {duplicate_count} duplicate rows ({dup_pct:.1f}%).")

        high_missing = [
            c for c, pct in missing_values.items()
            if th["missing_high"] * 100 < pct <= th["missing_drop"] * 100
        ]
        if high_missing:
            recs.append(
                f"HIGH: Handle {len(high_missing)} column(s) with 30-70% missing: "
                + ", ".join(high_missing[:3]) + (" ..." if len(high_missing) > 3 else "")
            )

        numeric_text = [
            c for c, iss in consistency_issues.items()
            if any("Numeric-like" in s for s in iss)
        ]
        if numeric_text:
            recs.append(
                f"HIGH: Convert numeric-like text to numbers in {len(numeric_text)} column(s): "
                + ", ".join(numeric_text[:3]) + (" ..." if len(numeric_text) > 3 else "")
            )

        moderate_missing = [
            c for c, pct in missing_values.items()
            if th["missing_medium"] * 100 < pct <= th["missing_high"] * 100
        ]
        if moderate_missing:
            recs.append(
                f"MEDIUM: Impute {len(moderate_missing)} column(s) with 10-30% missing: "
                + ", ".join(moderate_missing[:3]) + (" ..." if len(moderate_missing) > 3 else "")
            )

        if outlier_count > 0:
            recs.append(f"MEDIUM: Review {outlier_count} outlier value(s); consider capping or removal.")

        date_like = [
            c for c, iss in consistency_issues.items()
            if any("Date-like" in s for s in iss)
        ]
        if date_like:
            recs.append(
                f"MEDIUM: Parse datetime in {len(date_like)} column(s): "
                + ", ".join(date_like[:3]) + (" ..." if len(date_like) > 3 else "")
            )

        ws_cols = [c for c, iss in consistency_issues.items() if any("Whitespace" in s for s in iss)]
        if ws_cols:
            recs.append(
                f"INFO: Trim whitespace in {len(ws_cols)} column(s): "
                + ", ".join(ws_cols[:3]) + (" ..." if len(ws_cols) > 3 else "")
            )

        case_cols = [c for c, iss in consistency_issues.items() if any("Case inconsistency" in s for s in iss)]
        if case_cols:
            recs.append(
                f"INFO: Standardize case in {len(case_cols)} column(s): "
                + ", ".join(case_cols[:3]) + (" ..." if len(case_cols) > 3 else "")
            )

        low_q = [(c, s) for c, s in quality_scores.items() if s < 0.5]
        if low_q:
            low_q.sort(key=lambda x: x[1])
            recs.append(
                "QUALITY: Low-quality columns (score < 0.5): "
                + ", ".join([f"{c} ({s:.2f})" for c, s in low_q[:3]])
                + (" ..." if len(low_q) > 3 else "")
            )

        if not recs:
            recs.append("EXCELLENT: No major data quality issues detected!")

        return recs

    def _propose_actions(
        self,
        missing_values: Dict[str, float],
        consistency_issues: Dict[str, List[str]],
        cardinality: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        th = self.config["thresholds"]
        actions: List[Dict[str, Any]] = []

        for c, pct in missing_values.items():
            if pct > th["missing_drop"] * 100:
                actions.append({"column": c, "action": "drop_column", "reason": "missing>70%"})
            elif pct > th["missing_high"] * 100:
                actions.append({"column": c, "action": "impute", "strategy": "advanced", "reason": "missing 30–70%"})
            elif pct > th["missing_medium"] * 100:
                actions.append({"column": c, "action": "impute", "strategy": "simple", "reason": "missing 10–30%"})

        for c, iss in (consistency_issues or {}).items():
            if any("Numeric-like" in s for s in iss):
                actions.append({"column": c, "action": "cast_numeric", "coerce": True})
            if any("Date-like" in s for s in iss):
                actions.append({"column": c, "action": "parse_datetime"})
            if any("Whitespace" in s for s in iss):
                actions.append({"column": c, "action": "trim_whitespace"})
            if any("Case inconsistency" in s for s in iss):
                actions.append({"column": c, "action": "standardize_case", "mode": "lower"})

        for c, card in cardinality.items():
            if card == "constant":
                actions.append({"column": c, "action": "drop_column", "reason": "constant"})
            elif card == "unique":
                actions.append({"column": c, "action": "flag_id"})

        return actions

    # ------------------------------------------------------------------ #
    # Overall quality
    # ------------------------------------------------------------------ #
    def _assess_overall_quality(
        self,
        missing_values: Dict[str, float],
        duplicate_count: int,
        outlier_count: int,
        quality_scores: Dict[str, float],
        total_rows: int,
    ) -> DataQuality:
        avg_missing = float(np.mean(list(missing_values.values()))) if missing_values else 0.0
        dup_pct = duplicate_count / max(total_rows, 1) * 100
        outlier_pct = outlier_count / max(total_rows, 1) * 100
        avg_quality = float(np.mean(list(quality_scores.values()))) if quality_scores else 0.5

        if (avg_missing < 5 and dup_pct < 1 and outlier_pct < 1 and avg_quality > 0.8):
            return DataQuality.EXCELLENT
        elif (avg_missing < 15 and dup_pct < 5 and outlier_pct < 5 and avg_quality > 0.6):
            return DataQuality.GOOD
        elif (avg_missing < 40 and dup_pct < 20 and outlier_pct < 15 and avg_quality > 0.4):
            return DataQuality.FAIR
        else:
            return DataQuality.POOR
