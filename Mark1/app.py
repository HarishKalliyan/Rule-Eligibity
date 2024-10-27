from flask import Flask, request, render_template
import re

app = Flask(__name__)

class Node:
    """Class representing a node in the AST."""
    def __init__(self, operator, left=None, right=None, value=None):
        self.operator = operator  # e.g., 'AND', 'OR', etc.
        self.left = left          # Left child Node
        self.right = right        # Right child Node
        self.value = value        # Value for leaf nodes (e.g., comparisons)


def create_rule(rule_string):
    """Create a Node object representing the corresponding AST."""
    rule_string = rule_string.strip()
    if not rule_string:
        raise ValueError("Rule string is empty or only contains whitespace.")

    # Split rule string into tokens by capturing operators separately
    tokens = re.split(r"(\bAND\b|\bOR\b)", rule_string)
    tokens = [token.strip() for token in tokens if token.strip()]  # Remove empty spaces

    stack = []
    current_comparison = []

    for token in tokens:
        if token in ("AND", "OR"):
            # Process any pending comparison before the operator
            if len(current_comparison) == 3:
                attribute, operator, value = current_comparison
                stack.append(Node(operator='COMPARE', value=f'{attribute.lower()} {operator} {value}'))
                current_comparison = []
            elif len(current_comparison) > 0:
                raise ValueError(f"Incomplete comparison detected before logical operator '{token}'.")

            # Ensure there are at least two items in the stack for the operator to connect
            if len(stack) < 2:
                raise ValueError(f"Insufficient expressions in stack for logical operator '{token}'.")

            # Pop the last two expressions and create a new node for the logical operation
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(operator=token, left=left, right=right))
        
        else:
            # Split comparison expressions into attribute, operator, and value
            comparison_parts = re.split(r"(==|!=|>=|<=|>|<)", token)
            if len(comparison_parts) != 3:
                raise ValueError(f"Invalid comparison structure: '{token}'")
            
            attribute, operator, value = [part.strip() for part in comparison_parts]
            current_comparison = [attribute, operator, value]

            # Ensure we have a valid comparison and push it to the stack
            if len(current_comparison) == 3:
                stack.append(Node(operator='COMPARE', value=f'{attribute.lower()} {operator} {value}'))
                current_comparison = []

    # Final validation of the stack length
    if len(stack) == 1:
        return stack[0]  # Return the root of the AST
    elif len(stack) == 0:
        raise ValueError("Invalid rule structure: No valid expressions were found.")
    else:
        raise ValueError(f"Invalid rule structure: Final stack contains {len(stack)} items instead of 1. Stack: {stack}")


def combine_rules(rules, operator="AND"):
    """
    Combine a list of rule strings into a single AST using the specified operator.
    """
    if operator not in ("AND", "OR"):
        raise ValueError("Unsupported operator for combining rules. Use 'AND' or 'OR'.")
    
    ast_nodes = [create_rule(rule) for rule in rules]
    
    if len(ast_nodes) == 1:
        return ast_nodes[0]
    
    combined_ast = ast_nodes[0]
    for ast in ast_nodes[1:]:
        combined_ast = Node(operator=operator, left=combined_ast, right=ast)
    
    return combined_ast


def evaluate_rule(ast, data):
    """Evaluate the rule against the provided data."""
    if ast is None:
        return False

    if ast.operator == 'COMPARE':
        attribute, operator, value = ast.value.split()
        attribute = attribute.lower()
        
        if attribute not in data:
            raise ValueError(f"Data is missing required attribute '{attribute}'.")

        # Convert to int or string based on the data type of the provided value
        try:
            value = int(value) if value.isdigit() else str(value)
        except ValueError:
            raise ValueError(f"Invalid comparison value: '{value}'")

        if operator == '==':
            return data.get(attribute) == value
        elif operator == '!=':
            return data.get(attribute) != value
        elif operator == '>':
            return data.get(attribute) > value
        elif operator == '<':
            return data.get(attribute) < value
        elif operator == '>=':
            return data.get(attribute) >= value
        elif operator == '<=':
            return data.get(attribute) <= value
        else:
            raise ValueError(f"Unsupported operator '{operator}'.")

    elif ast.operator == 'AND':
        return evaluate_rule(ast.left, data) and evaluate_rule(ast.right, data)
    elif ast.operator == 'OR':
        return evaluate_rule(ast.left, data) or evaluate_rule(ast.right, data)
    else:
        raise ValueError(f"Unsupported logical operator '{ast.operator}'.")


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        rule = request.form.get('rule')
        age = request.form.get('age')
        department = request.form.get('department')
        income = request.form.get('income')
        spend = request.form.get('spend')
        
        try:
            rules = [rule]  # List of rules (add more rules if needed)
            combined_ast = combine_rules(rules, operator="AND")
            
            data = {
                'age': int(age),
                'department': department.lower(),
                'income': int(income),
                'spend': int(spend)
            }
            
            result = evaluate_rule(combined_ast, data)
        except Exception as e:
            error = f"Error: {e}"
    
    return render_template('index.html', result=result, error=error)


if __name__ == '__main__':
    app.run(debug=True)
