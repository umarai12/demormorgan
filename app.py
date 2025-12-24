import streamlit as st
import pandas as pd
import itertools
import re
from graphviz import Digraph

st.set_page_config(page_title="Advanced Logic Expression + Circuit", layout="wide")
st.title("⚡ Advanced Logic Expression + Circuit Visualizer")

st.markdown("""
### Rules:
- Operators: `and`, `or`, `not`, `xor`, `xnor`, `nand`, `nor`  
- Variables: uppercase letters A, B, C ...  
- Examples:  
  - `A and (not B or C)`  
  - `A xor B`  
  - `not (A and B) or C`  
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

# Map logical functions to Python
def safe_eval(expr, local_vars):
    mapping = {
        "and": lambda a,b: a and b,
        "or": lambda a,b: a or b,
        "not": lambda a: not a,
        "xor": lambda a,b: a != b,
        "xnor": lambda a,b: a == b,
        "nand": lambda a,b: not (a and b),
        "nor": lambda a,b: not (a or b)
    }
    # Replace operators with Python equivalents
    expr_py = expr
    for op in mapping.keys():
        expr_py = re.sub(r'\b'+op+r'\b', op, expr_py)
    # Safe eval with mapping
    local_dict = {**local_vars, **mapping}
    return eval(expr_py, {"__builtins__":None}, local_dict)

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
    st.error("Invalid expression! Follow the rules.")
    st.stop()

# -----------------------
# Logic Circuit Diagram
# -----------------------
st.subheader("💡 Logic Circuit Diagram")

dot = Digraph(comment='Logic Circuit', format='png')
gate_shapes = {
    "and":"box", "or":"ellipse", "not":"triangle",
    "xor":"parallelogram", "xnor":"diamond",
    "nand":"box", "nor":"ellipse"
}

# Add variable nodes
for var in variables:
    dot.node(var, var, shape='circle')

# Recursive function to parse and create gates
def add_nodes(expr, parent=None):
    expr = expr.strip()
    # Check NOT
    if expr.startswith("not "):
        node_id = f"NOT_{expr}"
        dot.node(node_id, "NOT", shape="triangle")
        if parent: dot.edge(node_id, parent)
        add_nodes(expr[4:], node_id)
    # XOR
    elif " xor " in expr:
        parts = expr.split(" xor ",1)
        node_id = f"XOR_{expr}"
        dot.node(node_id, "XOR", shape="parallelogram")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    # XNOR
    elif " xnor " in expr:
        parts = expr.split(" xnor ",1)
        node_id = f"XNOR_{expr}"
        dot.node(node_id, "XNOR", shape="diamond")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    # NAND
    elif " nand " in expr:
        parts = expr.split(" nand ",1)
        node_id = f"NAND_{expr}"
        dot.node(node_id, "NAND", shape="box")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    # NOR
    elif " nor " in expr:
        parts = expr.split(" nor ",1)
        node_id = f"NOR_{expr}"
        dot.node(node_id, "NOR", shape="ellipse")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    # AND
    elif " and " in expr:
        parts = expr.split(" and ",1)
        node_id = f"AND_{expr}"
        dot.node(node_id, "AND", shape="box")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    # OR
    elif " or " in expr:
        parts = expr.split(" or ",1)
        node_id = f"OR_{expr}"
        dot.node(node_id, "OR", shape="ellipse")
        if parent: dot.edge(node_id, parent)
        add_nodes(parts[0], node_id)
        add_nodes(parts[1], node_id)
    else:
        # Leaf variable
        if parent: dot.edge(expr, parent)

add_nodes(expr)
st.graphviz_chart(dot)
