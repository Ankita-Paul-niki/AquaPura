"""
AquaPura -- Knowledge base for the rule-based chatbot.

Architecture note
-----------------
This module is the only place that needs to change when upgrading to a
real LLM.  The chat router calls `get_reply(message, context)` and receives
a plain string back.  To swap in an LLM, replace the body of `get_reply`
with an API call and leave everything else untouched.

Current implementation
----------------------
Pure rule-based matching: each Rule has a list of trigger keywords and a
list of response strings (one is chosen at random to avoid feeling robotic).
Rules are checked in order; the first match wins.  A catch-all rule fires
when nothing matches.

Context awareness
-----------------
If the frontend passes a `prediction_context` dict (the most recent
PredictionResponse), the reply for result-related questions is generated
dynamically from the actual values rather than from a canned string.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class PredictionContext:
    """Subset of the frontend PredictionResponse that the chat endpoint accepts."""
    potable: bool
    potable_label: int
    probability_potable: Optional[float] = None
    probability_not_potable: Optional[float] = None


@dataclass
class Rule:
    """A single intent: list of keyword patterns and a list of candidate replies."""
    patterns: list[str]          # substrings / regex fragments to search for
    replies:  list[str]          # one is chosen at random on match
    needs_context: bool = False  # if True, only fire when context is present


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

_PARAM_RULES: list[Rule] = [
    Rule(
        patterns=["ph", "acid", "alkalin", "basic"],
        replies=[
            "**pH** measures how acidic or alkaline your water is on a scale of 0 to 14.\n\n"
            "- **< 7** = acidic\n- **7** = neutral\n- **> 7** = alkaline\n\n"
            "The WHO recommends a drinking-water pH of **6.5 – 8.5**. "
            "Very low pH can corrode pipes and leach metals; very high pH can cause scale build-up and taste issues."
        ],
    ),
    Rule(
        patterns=["hard", "calcium", "magnesium"],
        replies=[
            "**Hardness** reflects the concentration of dissolved calcium and magnesium, measured in mg/L.\n\n"
            "Hard water (> 300 mg/L) can leave scale on appliances and pipes. "
            "Soft water (< 60 mg/L) may be more corrosive. "
            "There is no WHO health-based guideline for hardness, but most people prefer 100 – 300 mg/L for taste."
        ],
    ),
    Rule(
        patterns=["solid", "tds", "dissolved solid"],
        replies=[
            "**Total Dissolved Solids (TDS)** is the total amount of minerals, salts, metals, and ions dissolved in water, measured in ppm (mg/L).\n\n"
            "The EPA secondary standard is **< 500 ppm** for taste. "
            "High TDS doesn't always mean unsafe water, but very high values can indicate contamination. "
            "The model uses TDS as one of nine features in its potability prediction."
        ],
    ),
    Rule(
        patterns=["chloramin", "disinfect"],
        replies=[
            "**Chloramines** are formed when ammonia is added to chlorine during water treatment. "
            "They are a common disinfectant used to kill bacteria and viruses.\n\n"
            "The EPA sets a maximum of **4 ppm** for chloramines in drinking water. "
            "At typical treatment levels they are considered safe, though some people are sensitive to taste or smell."
        ],
    ),
    Rule(
        patterns=["sulfat", "sulphat"],
        replies=[
            "**Sulfate** is a naturally occurring mineral dissolved in water, measured in mg/L.\n\n"
            "The EPA secondary standard for taste is **250 mg/L**. "
            "Very high levels (> 500 mg/L) may cause a laxative effect in some people. "
            "Sulfate is one of the three features with missing values in the training dataset — "
            "the model handles this internally using median imputation."
        ],
    ),
    Rule(
        patterns=["conduct"],
        replies=[
            "**Conductivity** measures how well water conducts electricity, in µS/cm. "
            "It is a proxy for the total amount of dissolved ions in the water.\n\n"
            "Pure distilled water has very low conductivity. "
            "Higher conductivity generally means more dissolved minerals. "
            "There is no single safe-level standard, but drinking water typically falls in the range **200 – 800 µS/cm**."
        ],
    ),
    Rule(
        patterns=["organic carbon", "carbon", "organic_carbon", "toc"],
        replies=[
            "**Organic Carbon (TOC)** refers to carbon-containing compounds from decomposed plant and animal matter, measured in ppm.\n\n"
            "High TOC can indicate contamination and may react with disinfectants to form harmful by-products (like trihalomethanes). "
            "The EPA action level is **2 ppm** for treated water. "
            "The training dataset's TOC values range from about 2 to 28 ppm."
        ],
    ),
    Rule(
        patterns=["trihalomethan", "thm", "chloroform", "by-product", "byproduct"],
        replies=[
            "**Trihalomethanes (THMs)** are chemical by-products formed when chlorine reacts with organic matter in water, measured in µg/L.\n\n"
            "They include chloroform and similar compounds. "
            "The EPA maximum contaminant level is **80 µg/L** for total THMs. "
            "Long-term exposure to high levels has been linked to health risks, which is why they are closely regulated."
        ],
    ),
    Rule(
        patterns=["turbid", "cloudy", "clarity", "ntu"],
        replies=[
            "**Turbidity** measures how cloudy or hazy the water looks, in NTU (Nephelometric Turbidity Units).\n\n"
            "Cloudy water is caused by suspended particles — sediment, bacteria, algae, or debris. "
            "The WHO guideline for drinking water is **< 1 NTU**. "
            "High turbidity can shield pathogens from disinfection and is often a sign of contamination."
        ],
    ),
]

_RESULT_RULES: list[Rule] = [
    Rule(
        patterns=["result", "mean", "what does", "explain", "classif", "predict", "outcome", "verdict"],
        replies=["DYNAMIC_RESULT"],
        needs_context=True,
    ),
    Rule(
        patterns=["not potable", "unsafe", "fail", "bad", "reject", "why not"],
        replies=["DYNAMIC_NOT_POTABLE"],
        needs_context=True,
    ),
    Rule(
        patterns=["potable", "safe", "pass", "good", "drink", "clean"],
        replies=["DYNAMIC_POTABLE"],
        needs_context=True,
    ),
    Rule(
        patterns=["probability", "confidence", "percent", "chance", "score", "likelihood"],
        replies=["DYNAMIC_PROBABILITY"],
        needs_context=True,
    ),
]

_ACTION_RULES: list[Rule] = [
    Rule(
        patterns=["what should i do", "next step", "action", "after result", "what now", "recommendation"],
        replies=[
            "Here are sensible next steps after receiving any AquaPura result:\n\n"
            "1. **Do not rely solely on this screening** — AquaPura is an educational ML tool, not a certified water test.\n"
            "2. **Send a sample to an accredited laboratory** for certified chemical and microbiological analysis.\n"
            "3. **Check local water quality reports** — most water utilities publish annual quality reports.\n"
            "4. **Contact your local water authority** if you are concerned about your supply.\n"
            "5. **Use point-of-use filters** (e.g. reverse osmosis) as a precautionary measure if certified testing is pending.\n\n"
            "⚠️ *AquaPura provides preliminary screening only and cannot certify that water is safe to drink.*"
        ],
    ),
    Rule(
        patterns=["improve", "fix", "treat", "filter", "purif", "solution", "reduce"],
        replies=[
            "Common water treatment approaches for specific issues:\n\n"
            "- **High turbidity or sediment** → Sediment filters or coagulation/flocculation\n"
            "- **Bacteria / pathogens** → Chlorination, UV treatment, or boiling\n"
            "- **High TDS or dissolved minerals** → Reverse osmosis or distillation\n"
            "- **High trihalomethanes** → Activated carbon filters (remove chlorine by-products)\n"
            "- **Low/high pH** → pH adjustment chemicals or neutralising filters\n\n"
            "Always consult a certified water treatment professional before making changes to your supply."
        ],
    ),
]

_GENERAL_RULES: list[Rule] = [
    Rule(
        patterns=["hello", "hi", "hey", "good morning", "good afternoon"],
        replies=[
            "Hello! I'm the **AquaPura AI Assistant**. 👋\n\n"
            "I can help you understand your water-quality assessment result, explain what each measurement means, "
            "or answer general questions about water quality.\n\n"
            "Try asking:\n"
            "- *What does my result mean?*\n"
            "- *What is pH?*\n"
            "- *Why was my sample classified as not potable?*\n"
            "- *What should I do after a not-potable result?*"
        ],
    ),
    Rule(
        patterns=["what can you do", "help", "what do you know", "capabilities", "how do you work"],
        replies=[
            "I'm the **AquaPura AI Assistant** — a knowledge-based chatbot built to help you understand water quality.\n\n"
            "I can:\n"
            "- **Explain each water parameter** (pH, hardness, TDS, chloramines, sulfate, conductivity, organic carbon, trihalomethanes, turbidity)\n"
            "- **Interpret your latest prediction result** (if you've already submitted a water sample)\n"
            "- **Suggest next steps** after receiving a potable or not-potable result\n"
            "- **Describe common water treatment approaches**\n\n"
            "I cannot certify water as safe to drink — always use accredited laboratory testing for safety decisions."
        ],
    ),
    Rule(
        patterns=["parameter", "which parameter", "what parameter", "all parameter", "list"],
        replies=[
            "AquaPura analyses **nine water-quality parameters**:\n\n"
            "1. **pH** — acidity/alkalinity (0–14)\n"
            "2. **Hardness** — dissolved calcium & magnesium (mg/L)\n"
            "3. **Solids (TDS)** — total dissolved solids (ppm)\n"
            "4. **Chloramines** — disinfectant level (ppm)\n"
            "5. **Sulfate** — naturally occurring mineral (mg/L)\n"
            "6. **Conductivity** — electrical conductivity (µS/cm)\n"
            "7. **Organic Carbon** — decayed organic matter (ppm)\n"
            "8. **Trihalomethanes** — disinfection by-products (µg/L)\n"
            "9. **Turbidity** — water cloudiness (NTU)\n\n"
            "Ask me about any of these for a detailed explanation."
        ],
    ),
    Rule(
        patterns=["model", "machine learning", "how does the model", "accuracy", "how accurate", "random forest"],
        replies=[
            "AquaPura uses a **Random Forest classifier** trained on the Kaggle Water Potability dataset (3,276 samples).\n\n"
            "**Training pipeline:**\n"
            "1. Median imputation (fills missing values using training-set medians)\n"
            "2. Random Forest with 300 trees and class-weight balancing\n\n"
            "**Performance on the held-out test set:**\n"
            "- Accuracy: 65%\n"
            "- ROC-AUC: 0.66\n"
            "- F1 (potable class): 0.48\n\n"
            "These numbers reflect the genuine difficulty of this dataset — all nine features have near-zero linear "
            "correlation with potability. The model is useful for educational screening, not clinical decisions."
        ],
    ),
    Rule(
        patterns=["sdg", "sustainable", "goal 6", "clean water", "sanitation"],
        replies=[
            "AquaPura is aligned with **UN Sustainable Development Goal 6: Clean Water and Sanitation**.\n\n"
            "SDG 6 aims to ensure availability and sustainable management of clean water and sanitation for all by 2030. "
            "Approximately 2 billion people still lack access to safe drinking water.\n\n"
            "AquaPura demonstrates how machine learning can assist in water-quality screening — a small step toward "
            "making water assessment tools more accessible and educational."
        ],
    ),
    Rule(
        patterns=["disclaimer", "certif", "safe to drink", "guarantee", "official", "laboratory"],
        replies=[
            "**Important disclaimer:**\n\n"
            "AquaPura provides **preliminary screening only**. The model was trained on a compiled research dataset "
            "and its labels are not certified by any water authority.\n\n"
            "A 'potable' prediction does **not** mean the water is certified safe to drink. "
            "A 'not potable' prediction does not mean the water is definitely unsafe.\n\n"
            "Always use **accredited laboratory analysis** before making any drinking-water safety decision."
        ],
    ),
    Rule(
        patterns=["thank", "thanks", "cheers", "great", "awesome", "helpful"],
        replies=[
            "You're welcome! 😊 Feel free to ask anything else about your water-quality results or the parameters.",
            "Happy to help! Remember — for certified results, always follow up with an accredited laboratory.",
        ],
    ),
]

# Ordered list of all rule groups (checked top-to-bottom)
_ALL_RULES: list[Rule] = (
    _RESULT_RULES + _ACTION_RULES + _PARAM_RULES + _GENERAL_RULES
)

_FALLBACK_REPLIES = [
    "I'm not sure I understood that. Could you rephrase?\n\n"
    "You can ask me things like:\n"
    "- *What does pH mean?*\n"
    "- *What does my result mean?*\n"
    "- *What should I do after a not-potable result?*\n"
    "- *Which parameters does AquaPura analyse?*",
]


# ---------------------------------------------------------------------------
# Dynamic reply generators
# ---------------------------------------------------------------------------

def _reply_for_result(ctx: PredictionContext) -> str:
    label = "**potable label**" if ctx.potable else "**not-potable label**"
    conf  = f"{round(ctx.probability_potable * 100)}%" if ctx.probability_potable is not None else "N/A"
    lines = [
        f"Your water sample was classified as {label} by AquaPura's Random Forest model.",
        "",
        f"- **Model class:** {ctx.potable_label} ({'potable' if ctx.potable else 'not potable'})",
        f"- **Model confidence (potable):** {conf}",
        "",
    ]
    if ctx.potable:
        lines += [
            "This means the model leaned toward the dataset's 'potable' class for your sample. "
            "However, this is a screening result only — it does **not** certify the water as safe to drink.",
        ]
    else:
        lines += [
            "This means the model leaned toward the dataset's 'not potable' class for your sample. "
            "This does **not** necessarily mean the water is unsafe — the model has a 65% test accuracy.",
            "",
            "Recommended next step: submit the sample to an accredited laboratory for certified analysis.",
        ]
    lines += ["", "⚠️ *AquaPura provides preliminary screening only.*"]
    return "\n".join(lines)


def _reply_for_not_potable(ctx: PredictionContext) -> str:
    if ctx.potable:
        return (
            "Your sample was actually classified as **potable** by the model. "
            "If you were expecting a not-potable result, double-check the values you entered.\n\n"
            "Remember: even a 'potable' label from AquaPura is not a safety guarantee — always verify with laboratory testing."
        )
    conf = f"{round((ctx.probability_not_potable or 0) * 100)}%"
    return (
        f"Your sample was classified as **not potable** with {conf} model confidence.\n\n"
        "Possible reasons the model flags a sample:\n"
        "- One or more parameters are at extreme values compared to the training data\n"
        "- A combination of moderately unusual readings that the model associates with the not-potable class\n\n"
        "The model does **not** identify which specific parameter caused the classification — "
        "it considers all nine features together.\n\n"
        "⚠️ *A not-potable result does not confirm the water is unsafe. Seek certified laboratory analysis.*"
    )


def _reply_for_potable(ctx: PredictionContext) -> str:
    if not ctx.potable:
        return (
            "Your sample was classified as **not potable** by the model. "
            "If you have questions about that result, ask *Why was my sample classified as not potable?*"
        )
    conf = f"{round((ctx.probability_potable or 0) * 100)}%"
    return (
        f"Your sample was classified as **potable** with {conf} model confidence.\n\n"
        "This means the model's Random Forest classifier assigned the dataset's 'potable' label "
        "based on all nine input measurements.\n\n"
        "⚠️ *A potable label does NOT certify the water is safe to drink. "
        "The model has a test accuracy of 65%. Always use accredited laboratory analysis for safety decisions.*"
    )


def _reply_for_probability(ctx: PredictionContext) -> str:
    pp  = f"{round((ctx.probability_potable or 0) * 100)}%"
    pnp = f"{round((ctx.probability_not_potable or 0) * 100)}%"
    return (
        f"The model returned these probability scores for your sample:\n\n"
        f"- **Potable label:** {pp}\n"
        f"- **Not-potable label:** {pnp}\n\n"
        "These are produced by the Random Forest classifier, which averages the votes of 300 decision trees. "
        "A score of 50% means the trees were evenly split.\n\n"
        "⚠️ *These probabilities reflect the model's confidence, not a guarantee of water safety.*"
    )


_DYNAMIC_MAP = {
    "DYNAMIC_RESULT":       _reply_for_result,
    "DYNAMIC_NOT_POTABLE":  _reply_for_not_potable,
    "DYNAMIC_POTABLE":      _reply_for_potable,
    "DYNAMIC_PROBABILITY":  _reply_for_probability,
}


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_reply(message: str, context: PredictionContext | None = None) -> str:
    """
    Return a reply string for the given user message.

    Parameters
    ----------
    message : str
        Raw text from the user.
    context : PredictionContext | None
        The user's most recent prediction result, if any.
        Used to generate context-aware replies for result-related questions.

    Returns
    -------
    str
        A plain-text / Markdown reply string.
        The frontend renders this with basic Markdown formatting.
    """
    if not message or not message.strip():
        return "Please type a message so I can help you."

    normalised = message.lower()
    # Remove punctuation for simpler matching
    normalised = re.sub(r"[^\w\s]", " ", normalised)

    for rule in _ALL_RULES:
        # Skip context-dependent rules when no context is available
        if rule.needs_context and context is None:
            continue

        for pattern in rule.patterns:
            if re.search(pattern, normalised):
                reply = random.choice(rule.replies)   # noqa: S311 — not cryptographic
                if reply in _DYNAMIC_MAP and context is not None:
                    return _DYNAMIC_MAP[reply](context)
                return reply

    # Try context-dependent result rules even when the question was vague,
    # as long as a context is present and no other rule matched.
    if context is not None:
        return _reply_for_result(context)

    return random.choice(_FALLBACK_REPLIES)   # noqa: S311
