# Symptom Tracker

A desktop app made with Python that helps students keep track of how they feel. You log your symptoms (headaches, tiredness, trouble concentrating) together with your daily habits (sleep, meals, water and exercise), and the app shows you simple patterns between them, along with basic habit recommendations.

> **Important:** this app does not diagnose anything and does not replace a doctor. It only looks at your own habits and gives general tips.

## Why we made it

A lot of students deal with the same symptoms again and again but never figure out why. Since they don't write anything down, it's hard to notice that, for example, they get a headache almost every time they sleep less than six hours. Our app collects that information in one place and makes those connections easy to see, so people can make better-informed decisions about their habits.

**Target audience:** high school and university students with irregular sleep and eating routines who want a simple way to monitor their well-being.

## Screenshots

| Daily log | History with filter |
|---|---|
| ![Daily log](capturas/1_registro_diario.png) | ![History filtered by symptom](capturas/3_historial_filtrado.png) |

| Patterns | Recommendations |
|---|---|
| ![Patterns chart](capturas/4_patrones.png) | ![Recommendations](capturas/5_recomendaciones.png) |

## Features

- **Daily log:** record the date, symptom, intensity (1 to 5), hours of sleep, meals, glasses of water and whether you exercised. Everything is validated, so invalid input shows a clear message instead of crashing the program.
- **History:** a table with all your records, from newest to oldest, with a summary of averages. You can **filter it by symptom** and delete a record you entered by mistake.
- **Pattern detection:** compares the days when a habit happens (for example, sleeping less than 6 hours) with the days when it doesn't, and shows the percentage of days with symptoms in each case. The results appear in a **bar chart** and in plain sentences.
- **Basic recommendations:** turns the detected patterns into simple habit suggestions, never a diagnosis.
- **Sample data:** one button loads 14 days of simulated data so you can try the app right away, and another one removes it without touching your real records.
- **Data persistence:** everything is saved in a CSV file, so your records are still there the next time you open the app.

## How to run it

### Requirements

- [Python 3.10 or newer](https://www.python.org/downloads/). During the installation, check the option that adds Python to PATH.
- Tkinter, the library used for the window. It comes included with Python on Windows and macOS. On some Linux systems it has to be installed separately (for example `sudo apt install python3-tk`).
- The libraries listed in `requirements.txt` (pandas and matplotlib).

### Steps

1. Download or clone this repository.
2. Open the project folder in Visual Studio Code (**File > Open Folder**).
3. Open a terminal in VS Code (**Terminal > New Terminal**) and install the libraries:

   ```
   pip install -r requirements.txt
   ```

4. Run the app:

   ```
   python main.py
   ```

   On some computers the commands are `pip3` and `python3` instead.

If VS Code says it can't find pandas or matplotlib, press **Ctrl+Shift+P**, choose **Python: Select Interpreter** and pick the same Python where you installed the libraries.

To try the patterns without waiting weeks to collect data, click **Cargar datos de ejemplo** (load sample data) at the top of the window.

## Project structure

```
rastreador-final/
├── main.py               # Starts the app
├── interfaz.py           # Graphical interface (Tkinter + matplotlib)
├── almacenamiento.py     # Reads and writes the CSV file (pandas)
├── analisis.py           # Summaries and pattern detection (pandas)
├── recomendaciones.py    # Basic recommendations for each pattern
├── requirements.txt      # Libraries needed to run the app
├── README.md
├── capturas/             # Screenshots of the app
└── datos/
    └── registros.csv     # Where the records are saved (one row per day)
```

### CSV format

| Column | What it stores |
|---|---|
| `fecha` | Date of the record (YYYY-MM-DD) |
| `sintoma` | none, headache, tiredness, lack of concentration or other (saved in Spanish) |
| `intensidad` | 0 if there were no symptoms, from 1 (mild) to 5 (very strong) otherwise |
| `sueno` | Hours of sleep |
| `comidas` | Meals during the day |
| `agua` | Glasses of water |
| `ejercicio` | `si` or `no` |
| `ejemplo` | `si` if the row comes from the sample data, `no` if you entered it |

If you log the same date twice, the existing record is updated instead of duplicated.

## Technical decisions

- **Tkinter for the interface.** It comes with Python, so nobody has to install anything extra, and it was enough to build tabs, forms and tables.
- **pandas for the data.** It reads and writes the CSV, filters the records and calculates averages and percentages with very little code, which keeps the analysis easy to read.
- **matplotlib for the chart.** It is embedded directly in the window, so the patterns are easier to understand than a list of numbers.
- **One CSV file instead of a database.** The project is small and a CSV is simple, readable (it even opens in Excel) and enough to keep the data between sessions.
- **Code split into modules.** `interfaz.py` only shows and asks for information. The logic lives in `almacenamiento.py` (files), `analisis.py` (patterns) and `recomendaciones.py` (tips), so each part can be changed without breaking the others.
- **Simple rules instead of AI.** A pattern is flagged when the share of days with symptoms is at least 20 points higher under a habit, and only if there are at least 3 days in each group. This is easy to explain and avoids drawing conclusions from very little data.
- **Robust against bad data.** The app validates every field, rejects future dates, and ignores damaged rows if someone edits the CSV by hand. If the file can't be written (for example, it is open in Excel), it shows an error message instead of crashing.
- **Paths that work from anywhere.** The location of the CSV is calculated from the code file, so the app works no matter which folder VS Code opens it from.

## Limitations

- The patterns are simple comparisons, not statistical proof. With few records they can be misleading, and a connection between two things does not mean one causes the other.
- It only looks at four habits and a short list of symptoms.
- It is a prototype made for a class. It is not a medical tool and it should not be used to decide on treatment.

## Team

| Name | Student ID | Contribution |
|---|---|---|
| [Name] | [ID] | [What this person worked on] |
| [Name] | [ID] | [What this person worked on] |
