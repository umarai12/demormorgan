import streamlit as st
import pandas as pd
import itertools
import re

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Unlimited Logical Expression Evaluator", layout="wide")
st.title("🧠 Unlimited Logical Expression Evaluator")
st.write("Enter any logical expression with AND / OR / NOT and get the truth table automatically.")

# -------------------------------
# Instructions
# -------------------------------
st.markdown("""
**Rules for typing expression:**
- Use lowercase operators: `and`, `or`, `not`
- Variables: uppercase letters `A, B, C, ...`
- Examples:
    - `A and B`
    - `not A or B`
    - `(A and B) or (C and not D)`
""")

# -------------------------------
# Expression Input
# -------------------------------
expr = st.text_input(
    "Enter logical expression (Unlimited variables):",
    value="not (A or B) and C"
)

# -------------------------------
# Detect Variables Automatically
# -------------------------------
variables = sorted(set(re.findall(r'\b[A-Z]\b', expr)))

if len(variables) == 0:
    st.warning("Please enter at least one variable (A, B, C...)")
    st.stop()

st.write("### Detected Variables:", ", ".join(variables))

# -------------------------------
# Generate All Possible Combinations
# -------------------------------
rows = list(itertools.product([0, 1], repeat=len(variables)))

# -------------------------------
# Evaluate Expression Securely
# -------------------------------
results = []

def safe_eval(expr, local_vars):
    return eval(
        expr,
        {"__builtins__": None},
        local_vars
    )

try:
    for row in rows:
        context = {var: bool(val) for var, val in zip(variables, row)}
        res = safe_eval(expr, context)
        results.append(1 if res else 0)

    # -------------------------------
    # Build DataFrame
    # -------------------------------
    table = {var: [row[i] for row in rows] for i, var in enumerate(variables)}
    table[expr] = results
    df = pd.DataFrame(table)

    # -------------------------------
    # Display Truth Table
    # -------------------------------
    st.subheader("📊 Truth Table")
    st.dataframe(df)

    st.success("Expression evaluated successfully ✔")

except Exception as e:
    st.error("❌ Invalid logical expression. Please follow the rules.")
    st.error(f"Details: {e}")

# -------------------------------
# Footer
# -------------------------------
st.write("---")
st.write("Made for DMS / Logical Expression assignments ✅ | By ChatGPT")
