"""Alpha 公式辅助生成引擎 — 三阶段表达式生成"""

import random
import uuid
from ..log_config import get_logger
from ..services.cache_service import get_cached_fields

logger = get_logger("alpha_generator")

# ── 预置字段（缓存为空时的 fallback） ──────────────────────────────

FALLBACK_FIELDS = [
    "close", "open", "high", "low", "volume", "returns",
    "market_cap", "pe_ratio", "pb_ratio", "ps_ratio",
    "dividend_yield", "earnings_per_share", "book_value_per_share",
    "revenue", "net_income", "operating_income",
    "total_assets", "total_liabilities", "current_ratio",
    "debt_to_equity", "roe", "roa", "gross_margin",
    "free_cash_flow", "enterprise_value", "beta",
    "volatility_30d", "price_momentum_6m", "short_interest",
    "implied_volatility", "avg_dollar_volume",
    "price_to_sales", "ev_to_ebitda", "earnings_yield",
    "revenue_growth", "earnings_growth",
]

GROUP_FIELDS = ["subindustry", "industry", "sector"]
TIME_WINDOWS = [5, 10, 20, 30, 40, 60, 90, 120, 250]
FILL_VALUES = ["0", "NaN", "rank(close)", "zscore(volume)"]

# ── 模板定义 ──────────────────────────────────────────────────────

STAGE1_TEMPLATES = [
    {"op": "rank",           "template": "rank({field})",                        "params": ["field"],          "category": "Cross Sectional"},
    {"op": "zscore",         "template": "zscore({field})",                      "params": ["field"],          "category": "Cross Sectional"},
    {"op": "scale",          "template": "scale({field})",                       "params": ["field"],          "category": "Cross Sectional"},
    {"op": "winsorize",      "template": "winsorize({field})",                   "params": ["field"],          "category": "Cross Sectional"},
    {"op": "normalize",      "template": "normalize({field})",                   "params": ["field"],          "category": "Cross Sectional"},
    {"op": "quantile",       "template": "quantile({field})",                    "params": ["field"],          "category": "Cross Sectional"},
    {"op": "abs",            "template": "abs({field})",                         "params": ["field"],          "category": "Arithmetic"},
    {"op": "inverse",        "template": "inverse({field})",                     "params": ["field"],          "category": "Arithmetic"},
    {"op": "log",            "template": "log({field})",                         "params": ["field"],          "category": "Arithmetic"},
    {"op": "sqrt",           "template": "sqrt({field})",                        "params": ["field"],          "category": "Arithmetic"},
    {"op": "sign",           "template": "sign({field})",                        "params": ["field"],          "category": "Arithmetic"},
    {"op": "group_rank",     "template": "group_rank({field}, {group})",         "params": ["field", "group"], "category": "Group"},
    {"op": "group_zscore",   "template": "group_zscore({field}, {group})",       "params": ["field", "group"], "category": "Group"},
    {"op": "group_mean",     "template": "group_mean({field}, 1, {group})",      "params": ["field", "group"], "category": "Group"},
    {"op": "ts_mean",        "template": "ts_mean({field}, {d})",                "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_std_dev",     "template": "ts_std_dev({field}, {d})",             "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_rank",        "template": "ts_rank({field}, {d})",                "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_zscore",      "template": "ts_zscore({field}, {d})",              "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_delta",       "template": "ts_delta({field}, {d})",               "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_sum",         "template": "ts_sum({field}, {d})",                 "params": ["field", "d"],     "category": "Time Series"},
    {"op": "ts_decay_linear","template": "ts_decay_linear({field}, {d})",        "params": ["field", "d"],     "category": "Time Series"},
    {"op": "add",            "template": "add({field_a}, {field_b})",            "params": ["field_a", "field_b"], "category": "Arithmetic"},
    {"op": "subtract",       "template": "subtract({field_a}, {field_b})",       "params": ["field_a", "field_b"], "category": "Arithmetic"},
    {"op": "multiply",       "template": "multiply({field_a}, {field_b})",       "params": ["field_a", "field_b"], "category": "Arithmetic"},
    {"op": "divide",         "template": "divide({field_a}, {field_b})",         "params": ["field_a", "field_b"], "category": "Arithmetic"},
]

STAGE2_TEMPLATES = [
    {"op": "ts_corr",         "template": "ts_corr({expr_a}, {expr_b}, {d})",         "params": ["expr_a", "expr_b", "d"],     "category": "Time Series"},
    {"op": "ts_covariance",   "template": "ts_covariance({expr_a}, {expr_b}, {d})",   "params": ["expr_a", "expr_b", "d"],     "category": "Time Series"},
    {"op": "ts_regression",   "template": "ts_regression({expr_a}, {expr_b}, {d})",   "params": ["expr_a", "expr_b", "d"],     "category": "Time Series"},
    {"op": "group_neutralize","template": "group_neutralize({expr_a}, {group})",       "params": ["expr_a", "group"],           "category": "Group"},
    {"op": "group_zscore",    "template": "group_zscore({expr_a}, {group})",           "params": ["expr_a", "group"],           "category": "Group"},
    {"op": "if_else",         "template": "if_else({expr_a} > 0.5, {expr_b}, {expr_c})","params": ["expr_a", "expr_b", "expr_c"], "category": "Logical"},
    {"op": "trade_when",      "template": "trade_when({expr_a}, {expr_b}, {fill})",   "params": ["expr_a", "expr_b", "fill"],  "category": "Transformational"},
    {"op": "add",             "template": "add({expr_a}, {expr_b})",                  "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "subtract",        "template": "subtract({expr_a}, {expr_b})",             "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "multiply",        "template": "multiply({expr_a}, {expr_b})",             "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "divide",          "template": "divide({expr_a}, {expr_b})",               "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "max",             "template": "max({expr_a}, {expr_b})",                  "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "min",             "template": "min({expr_a}, {expr_b})",                  "params": ["expr_a", "expr_b"],          "category": "Arithmetic"},
    {"op": "ts_decay_linear", "template": "ts_decay_linear({expr_a}, {d})",           "params": ["expr_a", "d"],               "category": "Time Series"},
    {"op": "ts_rank",         "template": "ts_rank({expr_a}, {d})",                   "params": ["expr_a", "d"],               "category": "Time Series"},
    {"op": "ts_zscore",       "template": "ts_zscore({expr_a}, {d})",                 "params": ["expr_a", "d"],               "category": "Time Series"},
]

STAGE3_TEMPLATES = [
    {"op": "group_rank",      "template": "group_rank({expr}, {group})",              "params": ["expr", "group"],  "category": "Group"},
    {"op": "group_zscore",    "template": "group_zscore({expr}, {group})",            "params": ["expr", "group"],  "category": "Group"},
    {"op": "group_neutralize","template": "group_neutralize({expr}, {group})",        "params": ["expr", "group"],  "category": "Group"},
    {"op": "zscore",          "template": "zscore({expr})",                            "params": ["expr"],           "category": "Cross Sectional"},
    {"op": "scale",           "template": "scale({expr})",                             "params": ["expr"],           "category": "Cross Sectional"},
    {"op": "winsorize",       "template": "winsorize({expr})",                         "params": ["expr"],           "category": "Cross Sectional"},
    {"op": "normalize",       "template": "normalize({expr})",                         "params": ["expr"],           "category": "Cross Sectional"},
    {"op": "ts_decay_linear", "template": "ts_decay_linear({expr}, {d})",              "params": ["expr", "d"],      "category": "Time Series"},
    {"op": "ts_mean",         "template": "ts_mean({expr}, {d})",                      "params": ["expr", "d"],      "category": "Time Series"},
]


# ── Helper ────────────────────────────────────────────────────────

def _gen_id(prefix: str = "gen") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _load_available_fields(dataset_ids: list[str]) -> list[str]:
    """从缓存加载字段，缓存为空时使用 fallback 列表。"""
    all_fields: set[str] = set()
    for ds_id in dataset_ids:
        cached = get_cached_fields(dataset_id=ds_id)
        for cf in cached:
            name = cf.get("name") or cf.get("id", "")
            if name:
                all_fields.add(name)
    if not all_fields:
        logger.warning("缓存字段为空，使用预置 fallback 字段列表")
        return list(FALLBACK_FIELDS)
    return sorted(all_fields)


# ── 模型 ──────────────────────────────────────────────────────────

from pydantic import BaseModel


class GenConfig(BaseModel):
    region: str = "USA"
    delay: int = 1
    universe: str = "TOP3000"
    instrument_type: str = "EQUITY"
    neutralization: str | None = None
    truncation: float | None = 0.08
    decay: int | None = None
    pasteurization: str | None = "ON"


class Stage1Expression(BaseModel):
    id: str
    formula: str
    operator: str
    field: str
    category: str
    params: dict


class Stage2Expression(BaseModel):
    id: str
    formula: str
    operator: str
    category: str
    composed_from: list[str]


class Stage3Expression(BaseModel):
    id: str
    formula: str
    operator: str
    category: str
    composed_from: list[str]


class Stage1Request(BaseModel):
    config: GenConfig
    dataset_ids: list[str]
    count: int = 10
    seed: int | None = None


class Stage1Response(BaseModel):
    expressions: list[Stage1Expression]
    fields_used: list[str]


class Stage2Request(BaseModel):
    input_expressions: list[Stage1Expression]
    count: int = 10
    seed: int | None = None


class Stage2Response(BaseModel):
    expressions: list[Stage2Expression]


class Stage3Request(BaseModel):
    input_expressions: list[Stage2Expression]
    count: int = 10
    seed: int | None = None


class Stage3Response(BaseModel):
    expressions: list[Stage3Expression]


# ── 生成函数 ──────────────────────────────────────────────────────


def generate_stage1(req: Stage1Request) -> Stage1Response:
    if req.seed is not None:
        random.seed(req.seed)

    fields = _load_available_fields(req.dataset_ids)
    random.shuffle(fields)

    # 确保有足够的字段
    selected_fields = list(fields)
    while len(selected_fields) < req.count:
        selected_fields.append(random.choice(fields))
    selected_fields = selected_fields[:req.count]

    expressions = []
    for field in selected_fields:
        tmpl = random.choice(STAGE1_TEMPLATES)
        params: dict = {}
        for p in tmpl["params"]:
            if p == "field":
                params[p] = field
            elif p == "field_a":
                params[p] = field
            elif p == "field_b":
                params[p] = random.choice(fields)
            elif p == "group":
                params[p] = random.choice(GROUP_FIELDS)
            elif p == "d":
                params[p] = str(random.choice(TIME_WINDOWS))
        formula = tmpl["template"].format(**params)

        expressions.append(Stage1Expression(
            id=_gen_id("s1"),
            formula=formula,
            operator=tmpl["op"],
            field=field,
            category=tmpl["category"],
            params=params,
        ))

    logger.info(f"Stage 1 生成: {len(expressions)} 个表达式")
    return Stage1Response(expressions=expressions, fields_used=selected_fields)


def generate_stage2(req: Stage2Request) -> Stage2Response:
    if not req.input_expressions:
        raise ValueError("Stage 2 需要至少一个 Stage 1 表达式作为输入")

    if req.seed is not None:
        random.seed(req.seed)

    inputs = req.input_expressions
    expressions = []
    for _ in range(req.count):
        tmpl = random.choice(STAGE2_TEMPLATES)
        params: dict = {}
        composed: list[str] = []

        if "expr_a" in tmpl["params"]:
            src = random.choice(inputs)
            params["expr_a"] = src.formula
            composed.append(src.id)
        if "expr_b" in tmpl["params"]:
            src = random.choice(inputs)
            params["expr_b"] = src.formula
            composed.append(src.id)
        if "expr_c" in tmpl["params"]:
            src = random.choice(inputs)
            params["expr_c"] = src.formula
            composed.append(src.id)
        if "group" in tmpl["params"]:
            params["group"] = random.choice(GROUP_FIELDS)
        if "d" in tmpl["params"]:
            params["d"] = str(random.choice(TIME_WINDOWS))
        if "fill" in tmpl["params"]:
            params["fill"] = random.choice(FILL_VALUES)

        formula = tmpl["template"].format(**params)
        expressions.append(Stage2Expression(
            id=_gen_id("s2"),
            formula=formula,
            operator=tmpl["op"],
            category=tmpl["category"],
            composed_from=list(set(composed)),
        ))

    logger.info(f"Stage 2 生成: {len(expressions)} 个表达式")
    return Stage2Response(expressions=expressions)


def generate_stage3(req: Stage3Request) -> Stage3Response:
    if not req.input_expressions:
        raise ValueError("Stage 3 需要至少一个 Stage 2 表达式作为输入")

    if req.seed is not None:
        random.seed(req.seed)

    inputs = req.input_expressions
    expressions = []
    for _ in range(req.count):
        tmpl = random.choice(STAGE3_TEMPLATES)
        src = random.choice(inputs)
        params = {"expr": src.formula}
        composed = [src.id]

        if "group" in tmpl["params"]:
            params["group"] = random.choice(GROUP_FIELDS)
        if "d" in tmpl["params"]:
            params["d"] = str(random.choice(TIME_WINDOWS))

        formula = tmpl["template"].format(**params)
        expressions.append(Stage3Expression(
            id=_gen_id("s3"),
            formula=formula,
            operator=tmpl["op"],
            category=tmpl["category"],
            composed_from=composed,
        ))

    logger.info(f"Stage 3 生成: {len(expressions)} 个表达式")
    return Stage3Response(expressions=expressions)
