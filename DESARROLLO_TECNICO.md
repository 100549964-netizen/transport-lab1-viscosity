# Laboratory 1 — Scientific programming workflow

## Objective

Develop and validate a reusable Python workflow for determining the apparent
viscosity of liquids from the upward motion of air bubbles. The workflow is
applied to experimental recordings of **water, glycerol and sunflower oil**,
using the instructor's glycerol recording for preliminary testing only.
GitHub Copilot was used as a programming assistant. Experimental choices,
measurements and scientific validation remain part of the laboratory analysis.

## Implementation and validation

| Stage | Implementation | Verification approach |
|---|---|---|
| 1. Video input | Native file picker and OpenCV video metadata | Original frame rate, dimensions, frame count and duration checked for each recording |
| 2. Spatial calibration | Two clicked reference marks at known separation; run-specific `calibration.json` | Pixel distance converted to cm/pixel and m/pixel; original-image coordinates retained |
| 3. Bubble tracking | Manual centre selection with enlarged view, timestamps from original frame indices, repeatable attempts | Displacement sign checked for upward motion; raw positions retained in CSV |
| 4. Motion analysis | Position–time plot and successive finite-difference velocities | Time axes in seconds, displacement in metres and velocity in m/s; terminal region chosen from graph |
| 5. Physical measurements | Four-point boundary radius measurements and independent liquid-density readings | Radius aspect ratio checked; at least five genuine density readings used for the density sample SD |
| 6. Viscosity and uncertainty | Approximate Stokes equation and first-order propagation of measured variability | Results in SI units; missing or non-circular measurements flagged rather than silently discarded |
| 7. Data export | Unique run and analysis directories with CSV, PNG and text outputs | Previous calibrations and tracking attempts retained without overwriting |

## Scientific calculations

Spatial calibration uses the measured ruler separation, `L`, and the distance
between the selected image points, `d_px`:

`scale_cm_per_pixel = L_cm / d_px`

For successive tracking points, upward displacement is calculated from the
reversed image y-axis. Interval velocities use the actual timestamps:

`v_i = (h_(i+1) - h_i) / (t_(i+1) - t_i)`

The terminal-speed estimate is the mean of an explicitly selected, approximately
constant-speed segment. Bubble radius is approximated from the horizontal and
vertical diameters, `R = sqrt(d_horizontal*d_vertical)/2`, with the run-specific
calibration applied. The approximate viscosity model is

`mu = 2*R^2*(rho_liquid-rho_air)*g/(9*v_terminal)`.

The reported propagated spread includes terms from repeated radius, liquid
density and selected velocity measurements. This is **not a comprehensive
uncertainty budget**: calibration bias, manual boundary selection, bubble
deformation and the applicability of the rigid-sphere Stokes model remain
important limitations.

## Experimental outputs

| Fluid | Density (kg/m³) | Equivalent radius (mm) | Selected speed (m/s) | Stokes estimate (Pa·s) |
|---|---:|---:|---:|---:|
| Water | 1048 ± 24.90 | 4.258 ± 0.195 | 0.19906 ± 0.00312 | 0.2079 ± 0.0199 |
| Glycerol | 1382 ± 66.11 | 3.049 ± 0.025 | 0.02822 ± 0.00146 | 0.9917 ± 0.0719 |
| Sunflower oil | 972 ± 46.58 | 2.221 ± 0.189 | 0.11874 ± 0.00055 | 0.0879 ± 0.0156 |

These are the software-reported results, not validated literature-equivalent
viscosities. At least one bubble-radius reading for each fluid was flagged
as strongly non-circular; accordingly the associated radius and viscosity
quality statuses remain **INCOMPLETE**. The analytical report discusses the
limitations rather than suppressing them.

## Traceability

The raw and calculated experiment data are supplied in `results/`, organised by
fluid, run ID and analysis ID. Full available GitHub Copilot prompt texts,
including intermediate corrections and development iterations, are in
`prompts.md`. The record contains two original headings without prompt bodies;
no missing instructions have been invented.
