# Monopoly Boycott Game (oTree)

This repository contains the oTree implementation of the **Monopoly Boycott Game**, developed for ECON 165 at UC Santa Cruz. The project idea originated from Jennifer Sotelo Perez, Isaac Robles, and Ryan Bradley.

## 🧠 Purpose
The experiment models a simple monopolist-consumer market, where:
- One **monopolist** sets a price each round.
- Multiple **consumers** decide whether to purchase or boycott.
- The game includes variants with different demand slopes (flat/step) and optional communication (chat) between consumers.

## 🧪 Experimental Structure
- Each session has 1 monopolist and multiple consumers.
- Rounds are grouped into blocks.
- Treatments can be toggled using session configs.

## 📁 Repo Contents
- `monopoly_boycott/` — main oTree app with game logic
  - `models.py` — defines players, groups, and payoff logic
  - `pages.py` — defines the sequence of pages shown to players
  - `templates/` — contains all HTML files for each page
- `settings.py` — oTree session configurations and defaults
- `requirements.txt` — list of dependencies
- `Procfile` — for deployment (e.g. on Heroku)

---

## 🧩 How It Works

1. The **monopolist** sets a price.
2. **Consumers** decide to buy or not.
3. Optionally, consumers can chat during certain rounds.
4. Payoffs:
   - Consumers get `endowment - price` if they buy.
   - Monopolist gets `price × number of buyers`.

---

## 🔧 Customization

You can change settings in `settings.py`:
- `use_chat=True` — enables consumer chat.
- `demand_slope='step'` or `'flat'` — controls how consumer values are assigned.
- `num_demo_participants=3` — adjust number of players in demo.

---

## ▶️ Running the Game Locally

### 1. Clone the repository
```bash
git clone https://github.com/vivianzvz/monopoly_boycott.git
cd monopoly_boycott
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the oTree dev server
```bash
otree devserver
```
