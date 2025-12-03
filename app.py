from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/nutrition", methods=["POST"])
def nutrition():
    data = request.json
    food = data.get("food")
    calories = len(food) * 10  # örnek hesap
    return jsonify({
        "food": food,
        "estimated_calories": calories
    })

if __name__ == "__main__":
    app.run(debug=True)
