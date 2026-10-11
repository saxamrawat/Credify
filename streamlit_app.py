"""Single-page analyst dashboard for risk scoring and review prioritization."""

from __future__ import annotations

import hashlib
import os

import numpy as np
import pandas as pd
import requests
import streamlit as st

from propensity_prediction.dashboard.client import (
    ReviewQueueAPIError,
    request_review_queue,
)
from propensity_prediction.dashboard.csv_input import (
    CSVInputError,
    read_customer_csv,
)


st.set_page_config(
    page_title="Portfolio Review | Credit Risk",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    .hero { padding: 1.4rem 1.6rem; border-radius: 1rem;
            background: linear-gradient(115deg, #10263f, #1c5268);
            color: white; margin-bottom: 1.2rem; }
    .hero h1 { color: white; margin: 0 0 .4rem 0; }
    .hero p { color: #d5e6ed; margin: 0; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Portfolio review</h1>
      <p>Score a customer file and prioritize a capacity-limited review queue.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "This tool estimates default risk for prioritization. It does not recommend "
    "or execute customer interventions."
)

api_base_url = st.text_input(
    "Scoring API address",
    value=os.getenv("PROPENSITY_API_URL", "http://127.0.0.1:8000"),
    help="Base URL of the FastAPI service. For local use, keep the default.",
)
uploaded_file = st.file_uploader(
    "Upload a prediction-time customer CSV",
    type=["csv"],
    help="Include ID and all 23 predictors. Do not include DEFAULT.",
)

customers = None
upload_digest = None
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    upload_digest = hashlib.sha256(file_bytes).hexdigest()
    try:
        customers = read_customer_csv(uploaded_file)
    except CSVInputError as exc:
        st.error(str(exc))

if customers is not None:
    st.success(
        f"File validated: {len(customers):,} customer rows and "
        f"{len(customers.columns)} expected columns."
    )
    with st.expander("Preview uploaded data", expanded=False):
        st.dataframe(customers.head(10), width="stretch", hide_index=True)

    control_col, summary_col = st.columns([1, 2])
    with control_col:
        max_review_count = st.number_input(
            "Maximum review count",
            min_value=0,
            value=min(10, len(customers)),
            step=1,
            help=(
                "The API accepts an absolute count. If equal-risk customers "
                "straddle the capacity boundary, the tied group is kept intact."
            ),
        )
    with summary_col:
        st.info(
            f"The model will score all **{len(customers):,}** customers. "
            f"The queue will target up to **{int(max_review_count):,}** reviews."
        )

    request_signature = (upload_digest, int(max_review_count), api_base_url.strip())
    if st.button("Score portfolio and build queue", type="primary", width="stretch"):
        if not api_base_url.strip():
            st.error("Enter the base address of the scoring API.")
        else:
            with st.spinner("Scoring the portfolio and applying the review capacity…"):
                try:
                    queue_response = request_review_queue(
                        customers=customers,
                        max_review_count=int(max_review_count),
                        api_base_url=api_base_url.strip(),
                    )
                    st.session_state["queue_result"] = queue_response
                    st.session_state["queue_signature"] = request_signature
                except ReviewQueueAPIError as exc:
                    st.session_state.pop("queue_result", None)
                    st.session_state.pop("queue_signature", None)
                    st.error(str(exc))

    if st.session_state.get("queue_signature") == request_signature:
        result = st.session_state["queue_result"]
        capacity = result["capacity"]
        metric_cols = st.columns(4)
        metric_cols[0].metric("Scored", f"{result['population_count']:,}")
        metric_cols[1].metric("Selected", f"{capacity['selected_count']:,}")
        metric_cols[2].metric("Target capacity", f"{capacity['target_review_count']:,}")
        metric_cols[3].metric("Unused capacity", f"{capacity['unused_capacity']:,}")

        result_frame = pd.DataFrame(result["customers"])
        selected_frame = result_frame[result_frame["selected_for_review"]]
        st.subheader("Risk distribution")
        histogram, edges = np.histogram(
            result_frame["predicted_default_probability"], bins=10, range=(0, 1)
        )
        chart_frame = pd.DataFrame(
            {"Probability range": [f"{left:.1f}–{right:.1f}" for left, right in zip(edges[:-1], edges[1:])],
             "Customers": histogram}
        ).set_index("Probability range")
        st.bar_chart(chart_frame, color="#168a91")

        st.subheader("Prioritized customer queue")
        if selected_frame.empty:
            st.info("No customers were selected at this capacity.")
        else:
            st.dataframe(
                selected_frame,
                width="stretch",
                hide_index=True,
                column_config={
                    "predicted_default_probability": st.column_config.NumberColumn(
                        "Predicted default probability", format="percent"
                    ),
                    "selected_for_review": st.column_config.CheckboxColumn(
                        "Selected for review"
                    ),
                },
            )

        with st.expander("Full ranked portfolio", expanded=False):
            st.dataframe(
                result_frame,
                width="stretch",
                hide_index=True,
                column_config={
                    "predicted_default_probability": st.column_config.NumberColumn(
                        "Predicted default probability", format="percent"
                    ),
                },
            )

        csv_bytes = result_frame.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download full ranked results (CSV)",
            data=csv_bytes,
            file_name="ranked_review_queue.csv",
            mime="text/csv",
            width="stretch",
        )
    elif st.session_state.get("queue_result") is not None:
        st.caption("Upload, capacity, or API address changed. Run scoring to refresh results.")

if uploaded_file is None:
    st.info("Upload a CSV to validate the portfolio and configure the review queue.")

with st.expander("API status"):
    if st.button("Check API health"):
        try:
            response = requests.get(
                f"{api_base_url.rstrip('/')}/health", timeout=(3, 10)
            )
            if response.ok:
                health = response.json()
                if health.get("model_loaded"):
                    st.success("Scoring API is ready and the model is loaded.")
                else:
                    st.warning("API is reachable, but the model artifact is unavailable.")
            else:
                st.error(f"API health endpoint returned HTTP {response.status_code}.")
        except requests.RequestException as exc:
            st.error(f"Could not reach the scoring API: {exc}")
