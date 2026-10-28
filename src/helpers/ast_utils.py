
"""Utilitaires pour interpréter des expressions mathématiques."""

import ast
import operator as op

OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def eval_expr(expr: str, variables: dict[str, float]) -> float:
    """Évalue une expression mathématique avec des variables autorisées."""

    def _eval(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(
                node.value, bool
            ):
                return node.value
            raise TypeError("Constante non autorisée")

        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise ValueError(f"Variable inconnue : {node.id}")
            return variables[node.id]

        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](
                _eval(node.left),
                _eval(node.right),
            )

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.operand))

        raise ValueError(
            f"Expression non autorisée : {ast.dump(node)}"
        )

    tree = ast.parse(expr.strip(), mode="eval")
    result = _eval(tree.body)

    if not isinstance(result, (int, float)) or isinstance(result, bool):
        raise TypeError("Le résultat doit être numérique")

    return float(result)
