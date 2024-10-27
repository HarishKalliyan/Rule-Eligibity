from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        if 'clear' in request.form:
            return render_template('index.html', result=None, error=None, request={'form': {}})
        
        rule = request.form.get('rule')
        age = request.form.get('age')
        department = request.form.get('department')
        income = request.form.get('income')
        spend = request.form.get('spend')
        
        missing_fields = []
        if not rule:
            missing_fields.append("Rule")
        if not age:
            missing_fields.append("Age")
        if not department:
            missing_fields.append("Department")
        if not income:
            missing_fields.append("Income")
        if not spend:
            missing_fields.append("Spend")
        
        if missing_fields:
            error = "The following fields are required: " + ", ".join(missing_fields)
        else:
            try:
                age = int(age)
                income = int(income)
                spend = int(spend)
                
                # Create a context dictionary for rule evaluation
                context = {
                    'age': age,
                    'department': department,
                    'income': income,
                    'spend': spend
                }
                
                # Replace AND/OR with and/or in the rule string
                rule = rule.replace('AND', 'and').replace('OR', 'or')
                
                # Evaluate the rule safely
                result = eval(rule, {"__builtins__": None}, context)
            except Exception as e:
                result = f"Error: {e}"
    
    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
