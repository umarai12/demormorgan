import streamlit as st
import pandas as pd
import itertools
import re
from graphviz import Digraph

st.set_page_config(page_title="Universal Logic Expression Visualizer", layout="wide")
st.title("Universal Logic Expression Visualizer (DMS)")

st.markdown("""
**Supported operators (lowercase):**  
`and, or, not, xor, xnor, nand, nor`  
Use parentheses `()` for nesting.
""")

# ----------------------------
# Helper Functions
# ----------------------------

def detect_variables(expr):
    tokens = re.findall(r'\b[A-Z]\b', expr)
    return sorted(set(tokens))

def eval_expr(expr, values):
    expr = expr.replace("xor", "^")
    expr = expr.replace("xnor", "==")
    expr = expr.replace("nand", "not (")
    expr = expr.replace("nor", "not (")
    
    for v, val in values.items():
        expr = expr.replace(v, str(bool(val)))

    expr = expr.replace("^", " != ")
    return int(eval(expr))

def generate_truth_table(expr, vars_):
    rows = []
    for combo in itertools.product([0, 1], repeat=len(vars_)):
        values = dict(zip(vars_, combo))
        try:
            result = eval_expr(expr, values)
        except:
            result = "Error"
        rows.append(list(combo) + [result])
    return pd.DataFrame(rows, columns=vars_ + ["Output"])

# ----------------------------
# Circuit Generator
# ----------------------------

def draw_circuit(expr):
    dot = Digraph()
    dot.attr(rankdir="LR")

    counter = 0

    def parse(e):
        nonlocal counter
        counter += 1
        node = f"N{counter}"

        if e.startswith("not"):
            child = parse(e[4:])
            dot.node(node, "NOT", shape="triangle")
            dot.edge(child, node)
            return node

        for op, label, shape in [
            (" and ", "AND", "box"),
            (" or ", "OR", "ellipse"),
            (" xor ", "XOR", "diamond"),
            (" nand ", "NAND", "box"),
            (" nor ", "NOR", "ellipse"),
            (" xnor ", "XNOR", "diamond")
        ]:
            if op in e:
                left, right = e.split(op, 1)
                l = parse(left.strip())
                r = parse(right.strip())
                dot.node(node, label, shape=shape)
                dot.edge(l, node)
                dot.edge(r, node)
                return node

        dot.node(node, e, shape="circle")
        return node

    output = parse(expr)
    dot.node("OUT", "OUTPUT", shape="circle")
    dot.edge(output, "OUT")

    return dot

# ----------------------------
# UI
# ----------------------------

expr = st.text_input(
    "Enter Logical Expression:",
    value="(A or B) or (not A and (A or B))"
)

if expr:
    vars_ = detect_variables(expr)

    if not vars_:
        st.error("No variables detected (use A, B, C...)")
    else:
        st.subheader("Detected Variables")
        st.write(vars_)

        st.subheader("Truth Table")
        df = generate_truth_table(expr, vars_)
        st.dataframe(df)

        st.subheader("Logic Circuit Diagram")
        st.graphviz_chart(draw_circuit(expr))
