from flask import Blueprint, render_template, request
from .logic import run_rebalancer

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index(): 
    if request.method == "POST":
        use_alpaca = request.form.get("use_alpaca") == "on"
        suggestions, portfolio_df = run_rebalancer(use_alpaca)
        return render_template("results.html", suggestions=suggestions, portfolio=portfolio_df.to_dict(orient="records"))
    return render_template("index.html")