# Transport Phenomena — Laboratory 1: Viscosity

## Project

Interactive Python analysis of rising air bubbles in **water**, **glycerol**, and **sunflower oil**. The code reads original videos, supports manual calibration and bubble tracking with an enlarged view, calculates position and velocity, estimates terminal velocity, allows radius and density measurements, and estimates viscosity using the approximate Stokes model. It saves CSV files, labelled PNG plots and a text summary for each experimental run.

The instructor's demonstration video is a **reference test**, not a replacement for the experimental recordings.

## Requirements

- Windows with a graphical desktop (native video picker uses Tkinter; interactive images use Matplotlib).
- Python 3.10+ with Tkinter available.
- Packages in `requirements.txt`: NumPy, Matplotlib, OpenCV (`opencv-python`).
- The **original** experimental video files (.mp4, .MOV, etc.) available locally. Large videos are deliberately excluded from this ZIP.

## Setup and run

Open a terminal in the directory containing `analyze_bubbles.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\analyze_bubbles.py
```

If PowerShell blocks the activation script, you can instead run ` .\.venv\Scripts\python.exe .\analyze_bubbles.py ` directly after installing packages into that environment.

## How to analyze a new fluid

1. Choose **Water**, **Glycerol**, or **Oil (sunflower oil)**.
2. Choose **Start a new experiment**, use the Windows file dialog to select the **original** recording, and confirm it.
3. Select a frame where a ruler or known length is visible. Click two calibration points; enter their *actual* separation in centimetres, then confirm and save `calibration.json`.
4. Follow the **same** rising bubble over a useful time interval. Choose the spacing in original video frames. For each frame, click near the bubble to enlarge the region, click its centre precisely, then accept/retry/skip. Save the tracking CSV.
5. Inspect the velocity plot and choose a **contiguous, approximately constant** section to estimate terminal velocity. If no credible section exists, report the result as incomplete.
6. Measure the radius in several distinct frames using the four bubble edges (left, right, top, bottom). Avoid guessing points when the outline is unclear.
7. Enter only genuine experimental density measurements in kg/m^3; five or more are required for the density standard deviation in the lab instructions.
8. Read the resulting comparison table and locate the CSV, plots and `summary.txt` under `results/<fluid>/<run_id>/analysis_<timestamp>_<id>/`.

To repeat tracking **without recalibrating**, choose the same fluid and **Continue an existing run from calibration.json**. New tracking attempts and analyses get different filenames/directories. Do not overwrite the original data.

## Files and reproducibility

- `analyze_bubbles.py`: main runnable scientific program.
- `requirements.txt`: Python dependencies.
- `results/`: saved run-specific calibration, manual tracking, plots, and numerical tables.
- `DESARROLLO_TECNICO.md`: concise description of methods, program development and result quality checks.
- `prompts.md`: available chronological Copilot instruction history, including intermediate changes and corrections.
- `.gitignore`: excludes large videos, local Python environments and caches from Git.

The calibration JSON files contain absolute paths to source videos on the
recording computer; those video files are intentionally excluded from this ZIP.
On another computer, choose the original recording again and perform a new
calibration before reproducing an experiment.

## Equations and limitations

For the model used in the class:

`mu = 2*R**2*(rho_liquid - rho_air)*g/(9*v_terminal)`, using SI units, `rho_air = 1.2 kg/m^3` and `g = 9.81 m/s^2`.

The reported `+/-` values use propagated **sample standard deviations** of radius, density (when 5+ real readings are present) and selected terminal velocities. This is **partial** uncertainty: calibration, image-selection bias, uncertainty in assumptions and systematic/model errors are not fully quantified. Bubbles flagged as strongly non-circular (>1.20 diameter ratio) yield `INCOMPLETE` radius/viscosity status. The rigid-sphere Stokes drag assumption is only approximate for gas bubbles, and wall effects/non-low-Reynolds flow may matter. Do not present flagged viscosity estimates as validated material-property measurements.

## Development documentation

`DESARROLLO_TECNICO.md` explains the implemented methods and validation checks.
`prompts.md` retains the available chronological history of instructions sent
to the AI coding assistant, including corrections. It is maintained separately
so the technical description is readable without losing the development record.

## What to submit (Guide 2)

Deliver the two-page scientific report **as a separate PDF**, full prompt history, runnable Python code ZIP (with README and requirements), and an accessible GitHub repository URL. Keep the GitHub repository and final code ZIP in sync. Do not upload large original videos to the code ZIP.
