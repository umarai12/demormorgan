import streamlit as st
import pandas as pd
import itertools
import re
from graphviz import Digraph

st.set_page_config(page_title="Logic Expression + Circuit Visualizer", layout="wide")
st.title("🧠 Logic Expression Evaluator + Circuit Visualizer")

st.markdown("""
### Rules:
- Operators: `and`, `or`, `not` (lowercase)  
- Variables: A, B, C ...  
- Example: `A and (not B or C)`
""")

expr = st.text_input("Enter logical expression:", value="A and (not B or C)")

# -----------------------
# Detect Variables
# -----------------------
variables = sorted(set(re.findall(r'\b[A-Z]\b', expr)))

if len(variables) == 0:
    st.warning("Enter at least one variable (A, B, C...)")
    st.stop()

st.write("Detected variables:", ", ".join(variables))

# -----------------------
# Generate Truth Table
# -----------------------
rows = list(itertools.product([0,1], repeat=len(variables)))
results = []

def safe_eval(expr, local_vars):
    return eval(expr, {"__builtins__": None}, local_vars)

try:
    for row in rows:
        context = {var: bool(val) for var,val in zip(variables,row)}
        res = safe_eval(expr, context)
        results.append(1 if res else 0)

    df = pd.DataFrame({var:[row[i] for row in rows] for i,var in enumerate(variables)})
    df[expr] = results
    st.subheader("📊 Truth Table")
    st.dataframe(df)

except Exception as e:
    st.error("Invalid expression!")
    st.stop()

# -----------------------
# Generate Logic Circuit using Graphviz
# -----------------------
st.subheader("💡 Logic Circuit Diagram")

dot = Digraph(comment='Logic Circuit')

# Add variable nodes
for var in variables:
    dot.node(var, var, shape='circle')

# Simple parser for AND/OR/NOT (visual only)
# Note: This is basic, for complex nested expressions you may need proper parser
def add_nodes(expr, parent=None):
    expr = expr.strip()
    if expr.startswith("not "):
        node_id = f"NOT_{expr}"
        dot.node(node_id, "NOT", shape="invtriangle")
        if parent:
            dot.edge(node_id, parent)
        inner = expr[4:]
        add_nodes(inner, node_id)
    elif " and " in expr:
        parts = expr.split(" and ", 1)
        node_id = f"AND_{expr}"
        dot.node(node_id, "AND", shape="box")
        if parent:
            dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    elif " or " in expr:
        parts = expr.split(" or ", 1)
        node_id = f"OR_{expr}"
        dot.node(node_id, "OR", shape="box")
        if parent:
            dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    else:
        # Leaf variable
        if parent:
            dot.edge(expr, parent)

add_nodes(expr)

st.graphviz_chart(dot)
