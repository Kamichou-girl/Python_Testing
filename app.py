import json

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "your-secret-key-here"


# Charger les données des clubs et compétitions
def load_clubs():
    with open("clubs.json") as c:
        list_of_clubs = json.load(c)["clubs"]
        return list_of_clubs


def load_competitions():
    with open("competitions.json") as comps:
        list_of_competitions = json.load(comps)["competitions"]
        return list_of_competitions


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    email = request.form["email"]
    clubs = load_clubs()
    competitions = load_competitions()

    # Trouver le club correspondant à l'email
    club = None
    for c in clubs:
        if c["email"] == email:
            club = c
            break

    if club is None:
        flash("Email non trouvé. Veuillez réessayer.")
        return redirect(url_for("index"))

    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    competitions = load_competitions()
    clubs = load_clubs()

    found_club = None
    found_competition = None

    for c in clubs:
        if c["name"] == club:
            found_club = c
            break

    for comp in competitions:
        if comp["name"] == competition:
            found_competition = comp
            break

    if found_club is None or found_competition is None:
        flash("Club ou compétition non trouvé.")
        return redirect(url_for("index"))

    return render_template(
        "booking.html", club=found_club, competition=found_competition
    )


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    competitions = load_competitions()
    clubs = load_clubs()

    competition_name = request.form["competition"]
    club_name = request.form["club"]
    places_required = int(request.form["places"])

    # Trouver le club et la compétition
    found_club = None
    found_competition = None

    for c in clubs:
        if c["name"] == club_name:
            found_club = c
            break

    for comp in competitions:
        if comp["name"] == competition_name:
            found_competition = comp
            break

    if found_club is None or found_competition is None:
        flash("Club ou compétition non trouvé.")
        return redirect(url_for("index"))

    # Vérifications
    if places_required > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places.")
        return render_template(
            "booking.html", club=found_club, competition=found_competition
        )

    if places_required > int(found_club["points"]):
        flash("Vous n'avez pas assez de points.")
        return render_template(
            "booking.html", club=found_club, competition=found_competition
        )

    if places_required > int(found_competition["numberOfPlaces"]):
        flash("Il n'y a pas assez de places disponibles.")
        return render_template(
            "booking.html", club=found_club, competition=found_competition
        )

    # Mettre à jour les données
    found_club["points"] = str(int(found_club["points"]) - places_required)
    found_competition["numberOfPlaces"] = str(
        int(found_competition["numberOfPlaces"]) - places_required
    )

    # Sauvegarder les données
    with open("clubs.json", "w") as c:
        json.dump({"clubs": clubs}, c)

    with open("competitions.json", "w") as comps:
        json.dump({"competitions": competitions}, comps)

    flash(f"Réservation réussie ! {places_required} places réservées.")
    return render_template("welcome.html", club=found_club, competitions=competitions)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
