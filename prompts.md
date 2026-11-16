# Laboratory 1 — Complete available prompt history

**Purpose.** Chronological record of the Copilot instructions available from the original
prompt document supplied by the student, supplemented with the zoom and final
integration instructions recovered from the project conversation.

This is the **full available history**, not a handpicked selection. The original supplied
document is preserved unmodified as `PROMPTS_ORIGINALES_APORTADOS.md`.
`PROCESO_Y_PROMPTS_CLAVE.md` is a short reading guide that highlights main milestones
but does not replace this history.

**Source caveat:** the supplied document contains two section headings without prompt
bodies (position-versus-time and repeated-radius measurement), and some numbering
gaps. Their exact missing text has not been invented. Additional Copilot messages
not in the supplied document or recoverable conversation cannot be certified here.

**Scientific context:** the glycerol calculations in the early prompts were exploratory
tests using the instructor's video. The final project code was then adapted to the
student's own water, glycerol and **sunflower-oil** videos. One original prompt
mistakenly uses "olive oil"; it is retained verbatim as historical text.

---

Create setup_check.py. Import NumPy, Matplotlib and OpenCV (cv2), and print their versions. Use NumPy to create x = 0, 1, 2, 3, 4 and plot y = x squared. Label the axes, save setup_check.png and display the plot. Also create requirements.txt listing numpy, matplotlib and opencv-python. Use the selected Python interpreter; do not install packages or change unrelated files.

---

Modify the existing setup_check.py script to add visible circular markers at each data point on the y = x squared graph. Keep the same calculations, axis labels and output filename setup_check.png. Do not create a new script or change unrelated files. Do not install any packages.

---

LOAD GLYCEROL VIDEO:Create a simple Python script called video_check.py for Laboratory 1 (Viscosity). Use OpenCV (cv2) to open my experimental video called 'fluids glycerol.MOV'. Use a file selection dialog so I can choose the video from my computer without moving it into my GitHub project. Check that the video opens successfully. Print the frame rate (fps), total number of frames, video duration in seconds, width and height in pixels. Read the first frame, save it as glycerol_first_frame.png in the project folder, and display it using Matplotlib with the correct RGB colors. Include clear error messages if the video cannot be opened or the first frame cannot be read. Keep the code short and readable. Do not modify existing scripts or install packages. Do not analyze bubble motion yet.

---

INSPECT GLYCEROL VIDEO:Modify the existing video_check.py for Laboratory 1 (Viscosity). The glycerol video loads correctly. It has 285 frames, a frame rate of approximately 29.99 fps, and a duration of 9.50 seconds. Now I want to inspect the video to identify the rising air bubble. Please:

1\. Keep the existing video file selection dialog.

2\. Extract four frames at approximately 0, 3, 6, and 9 seconds.

3\. Display these four frames side by side using Matplotlib, maintaining the correct aspect ratio and RGB colors.

4\. Add a title above each frame showing its time in seconds.

5\. Save the combined figure as glycerol_sample_frames.png.

6\. Do not calculate velocity, viscosity, or bubble radius yet.

7\. Keep the program simple, readable, and use only the libraries already installed.

Do not change unrelated files or install new packages

---

5.ZOOM IN TO GLYCEROL BUBBLES:Create a new Python script called bubble_inspection.py for Laboratory 1 – Viscosity.

My glycerol video has a resolution of 720 × 1280 pixels and a frame rate of approximately 29.99 fps. I want to identify the rising air bubbles more clearly before measuring anything.

Please: Use OpenCV to load the video using a file selection dialog. Extract frames at 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5 and 7.0 seconds. Crop each frame horizontally between approximately x = 260 and x = 480 pixels, keeping the vertical section containing the graduated cylinder. Arrange these eight cropped frames in a large 2 × 4 Matplotlib figure. Label every frame with its exact video time in seconds. Preserve the image aspect ratio and correct RGB colors.Save the figure as glycerol_bubble_closeups.png. Make the images large and clear enough to distinguish individual bubbles. Do not calculate velocity, bubble radius or viscosity yet. Do not modify video_check.py or other existing scripts. Do not install additional packages.

---

MANUAL TRACKING OF ONE SINGLE BUBBLE:Prompt 6 — Manual bubble tracking in glycerol video



Create a new Python script called track_bubble_manual.py for Laboratory 1 – Viscosity.



I have already confirmed that the glycerol video opens correctly and that a rising bubble is visible.



Now I want a simple manual tracking tool for one bubble.



Please:

1\. Use a file selection dialog to choose the glycerol video.

2\. Ask me for:

   - a start time in seconds,

   - an end time in seconds,

   - and a time step in seconds between frames.

3\. Extract frames from that time interval.

4\. For each frame, display the cropped cylinder region so the bubble is large and easy to see.

5\. Let me click once on the center of the same bubble in each frame.

6\. Store for each click:

   - frame index,

   - time in seconds,

   - x position in pixels,

   - y position in pixels.

7\. Save the results to a CSV file called glycerol_bubble_tracking.csv.

8\. Also save a figure called glycerol_tracking_overview\.png showing the clicked points over the displayed frames.

9\. Keep the code simple and readable.

10\. Use only the libraries already installed.

11\. Do not calculate velocity, radius, or viscosity yet.

Do not modify unrelated files and do not install new packages.

---

7\. GLYCEROL VIDEO CALIBRATION:Create a new Python script called calibrate_glycerol.py for Laboratory 1 – Viscosity.

I have measured the real vertical distance between the 20 mL and 100 mL graduation marks on my cylinder using a centimetre ruler.

The measured distance is 14.3 cm.

I need to calibrate my original glycerol video so I can convert pixels into centimetres.

Please:

1\. Use OpenCV to open my glycerol video through a file selection dialog. Extract and display the frame at approximately 4.0 seconds at its original resolution of 720 × 1280 pixels. Display the image using Matplotlib and allow me to zoom in if necessary. Ask me to click exactly on the horizontal graduation line corresponding to 100 mL. Then ask me to click on the horizontal graduation line corresponding to 20 mL. Record the original image pixel coordinates of both selected points, even if the displayed figure is zoomed. Calculate the vertical pixel distance as abs(y_100 - y_20). Calculate the spatial calibration factor using:

   calibration_factor = 14.3 / pixel_distance

   The units must be cm/pixel. Print the selected pixel coordinates, pixel distance, and calibration factor. Save the calibration factor and selected coordinates to a file named glycerol_calibration.json. Save an annotated image named glycerol_calibration.png showing both selected points and the measured distance.

Do not calculate velocity, bubble radius, or viscosity yet.

Do not modify the existing tracking CSV or unrelated Python scripts.

Keep the program simple

---

9.CHANGE 1 FOTOGRAMA PER 10 SECONDS:I need to correct an important detail in my Laboratory 1 bubble-tracking analysis.

The original glycerol video was recorded at approximately 29.99 fps.

My professor wants us to analyze ONE FRAME EVERY 10 ORIGINAL FRAMES, NOT convert the video to 10 fps.

Please modify track_bubble_manual.py so that:

1\. It opens the ORIGINAL video, "fluids glycerol.MOV".

2\. It preserves the original video frame rate of approximately 29.99 fps.

3\. It selects one frame every 10 original frames, using frame indices that differ by exactly 10.

4\. It calculates each timestamp using the original frame index divided by the original video fps.

5\. It lets me manually click the center of the same bubble in each selected frame.

6\. It saves the measurements as glycerol_tracking_every10frames.csv.

7\. It saves a tracking overview figure as glycerol_tracking_every10frames.png.

8\. It preserves original full-frame pixel coordinates so that I can reuse my existing calibration factor.

9\. It does not overwrite any previous measurement or calibration files.

For now, only implement the frame selection and manual tracking. Do not calculate velocity or viscosity.

Do not convert the video or change its fps.

Keep the code simple and do not install additional libraries.

---

10.POSITIONVSTIME:

_[Only a heading was present in the supplied history; the full prompt text is unavailable in that source.]_

---

11VELOCITY:Create a new Python script called glycerol_velocity.py for Laboratory 1 – Viscosity.



I have already successfully calculated the position of a rising air bubble in glycerol.



My verified position data are stored in glycerol_position_every10frames.csv.



The original video was recorded at approximately 29.99 fps, and I selected one frame every 10 original frames.



I now want to calculate the bubble's velocity as a function of time.



Please:



1\. Load glycerol_position_every10frames.csv.

2\. Identify the time column in seconds and the upward displacement column in centimetres. Check the CSV headers rather than assuming their names.

3\. Calculate the velocity between each pair of consecutive measurements using:



   velocity = (position[i+1] - position[i]) / (time[i+1] - time[i])



4\. Calculate the midpoint time for each velocity measurement:



   midpoint_time = (time[i+1] + time[i]) / 2



5\. Print a table containing midpoint time (s), displacement between frames (cm), time interval (s), and velocity (cm/s).

6\. Create a graph of velocity (cm/s) versus midpoint time (s), using circular markers connected by a line.

7\. Label both axes correctly.

8\. Use the title "Glycerol Bubble – Velocity vs. Time".

9\. Save the graph as glycerol_velocity_every10frames.png.

10\. Save the numerical results as glycerol_velocity_every10frames.csv.

11\. Calculate and print the average velocity over the complete tracked interval as total upward displacement divided by total elapsed time.

12\. Verify that the velocities are positive and that the time intervals are approximately 0.334 seconds.

13\. Print a clear warning if one velocity differs substantially from the others, but do not automatically remove any measurements.

Do not calculate terminal velocity, viscosity, or uncertainty yet.

Do not overwrite the original tracking, calibration, or position data.

Keep the program simple and readable. Do not install additional libraries.

---

12.WHY LAST POINT IS HIGHER:Create a new Python script called verify_glycerol_last_frames.py for Laboratory 1 – Viscosity.



My velocity graph shows that the final velocity measurement at approximately 6.169 seconds is 5.604 cm/s, which is 18.1% above the median velocity of 4.746 cm/s.



Before estimating terminal velocity, I want to investigate whether the last bubble positions were selected correctly.



Please:



1\. Open my original video "fluids glycerol.MOV" using a file selection dialog.

2\. Load the measurements from glycerol_tracking_every10frames.csv.

3\. Extract original video frames 160, 170, 180 and 190.

4\. Crop the images around the cylinder and enlarge them for detailed inspection.

5\. Mark the previously selected bubble center in each frame with a red circle.

6\. Display the four frames side by side, labelled with their frame numbers and times.

7\. Save the figure as glycerol_last_frames_verification.png.

8\. Print the vertical displacement in pixels between frames 160–170, 170–180 and 180–190.

9\. Do not automatically modify, delete or exclude any measurement.

10\. Do not calculate viscosity yet.



Use only the libraries already installed and keep the script simple and readable.

---

13:ESTIMATE GLYCEROL TERMINAL VELOCITY:Create a new Python script called glycerol_terminal_velocity.py for Laboratory 1 – Viscosity.



I have calculated the velocity of a rising air bubble in glycerol using one frame every 10 original frames.



The results are saved in glycerol_velocity_every10frames.csv.



The velocity graph shows that the first six interval velocities are approximately constant, while the final interval is about 18% higher than the median.



I want to estimate the terminal velocity scientifically without automatically deleting any measurements.



Please:



1\. Load glycerol_velocity_every10frames.csv and identify the time and velocity columns.

2\. Print all seven velocity measurements.

3\. Calculate the mean velocity and sample standard deviation of the first six intervals as a candidate constant-speed region.

4\. Calculate the mean velocity and sample standard deviation using all seven intervals for comparison.

5\. Print the median velocity of the complete dataset.

6\. Explain numerically how much the final velocity differs from the mean of the first six intervals.

7\. Generate a velocity vs. time graph highlighting the first six intervals as the candidate terminal-velocity region.

8\. Include a horizontal dashed line showing the mean velocity of that region.

9\. Clearly mark the final measurement as a point requiring further inspection, without deleting it.

10\. Save the graph as glycerol_terminal_velocity.png.

11\. Save the numerical summary as glycerol_terminal_velocity_summary.csv.

12\. Display both estimates with units of cm/s.

13\. Do not automatically claim that terminal velocity has been definitively reached. Label the result as a provisional estimate based on the approximately constant-speed region.



Do not modify or overwrite any original measurements.



Do not calculate viscosity yet.



Keep the code short and readable. Do not install additional libraries.

---

14BUBBLE RADIUS:Create a new Python script called glycerol_bubble_radius.py for Laboratory 1 – Viscosity.



I have already tracked a rising air bubble in glycerol and calibrated the video.



My files are:

\- fluids glycerol.MOV (original video, approximately 29.99 fps)

\- glycerol_tracking_every10frames.csv

\- glycerol_calibration.json



I want to measure the radius of the SAME bubble that I previously tracked.



For this first test, use original video frame 130, corresponding to approximately 4.335 seconds.



Please:



1\. Open the original glycerol video through a file selection dialog.

2\. Load frame 130 at its original resolution of 720 × 1280 pixels.

3\. Load the tracked bubble center for frame 130 from glycerol_tracking_every10frames.csv.

4\. Crop and enlarge the image around the tracked bubble center, leaving enough space to see its complete boundary.

5\. Display the enlarged bubble clearly using Matplotlib.

6\. Allow me to manually select four points on the bubble boundary in this order:

   - Left edge

   - Right edge

   - Top edge

   - Bottom edge

7\. Calculate the horizontal and vertical diameters in ORIGINAL image pixels, accounting correctly for any cropping or display enlargement.

8\. Calculate the equivalent bubble radius in pixels using:



   radius_pixels = sqrt(horizontal_diameter_pixels \* vertical_diameter_pixels) / 2



9\. Load the calibration factor from glycerol_calibration.json rather than hardcoding it.

10\. Convert the radius to centimetres and metres.

11\. Print the horizontal diameter, vertical diameter, radius in pixels, radius in cm, and radius in metres.

12\. Calculate and print the horizontal-to-vertical diameter ratio to help assess how circular the bubble is.

13\. Save the numerical measurements as glycerol_radius_test.csv.

14\. Save an annotated image as glycerol_radius_test.png showing the four selected points and the measured diameters.

15\. Allow me to retry the selection if I click incorrectly.



Do not calculate viscosity yet.



Do not overwrite any existing calibration, tracking, position or velocity files.



Use only the libraries already installed, and keep the code simple and readable.

---

15.MEASUREMENT OF RADIUS IN DIFFERENT FRAMES:

_[Only a heading was present in the supplied history; the full prompt text is unavailable in that source.]_

---

16GLYCEROL DENSITY CALCULATION:Create a new Python script called glycerol_density.py for Laboratory 1 – Viscosity.



I have already measured the bubble radius and terminal velocity. Now I need to calculate the glycerol density and its experimental standard deviation.



My professor requires at least five experimental density measurements.



Please:



1\. Ask me to enter at least five experimental measurements.

2\. For each measurement, ask for:

   - Mass of the empty container in grams.

   - Mass of the container with glycerol in grams.

   - Volume of glycerol in mL.

3\. Calculate the mass of glycerol by subtracting the empty container mass from the total mass.

4\. Calculate density for each measurement using:



   density = glycerol_mass / glycerol_volume



5\. Express density in g/cm³ and kg/m³.

6\. Calculate the mean density.

7\. Calculate the SAMPLE standard deviation using ddof=1.

8\. Print a table containing all individual measurements and calculated densities.

9\. Report the result as mean density ± sample standard deviation.

10\. Save all measurements as glycerol_density_measurements.csv.

11\. Save the mean, sample standard deviation and number of measurements as glycerol_density_summary.csv.

12\. Check that all masses and volumes are physically valid and positive.

13\. Never invent, substitute or automatically generate experimental measurements.



Do not calculate viscosity yet.



Do not modify my existing radius, velocity, calibration or tracking files.



Use only NumPy and standard Python libraries. Keep the code simple and readable.

---

17.VISCOSITY CALCULATION:Create a new Python script called glycerol_viscosity.py for Laboratory 1 – Viscosity.



I have measured the bubble radius, estimated the terminal velocity, and obtained one experimental glycerol density measurement.



My available results are:



\- Mean bubble radius: 0.3528 cm

\- Provisional terminal velocity: 4.754 cm/s

\- Experimentally measured glycerol density from one trial: 1440 kg/m³

\- Assumed air density: 1.2 kg/m³

\- Gravitational acceleration: 9.81 m/s²



Important: A previous five-value density dataset included simulated measurements. Do not use it as genuine experimental data.



Please:



1\. Create a short and readable Python program to calculate glycerol viscosity using Stokes' law.



2\. Use the formula:



   mu = (2 \* R\*\*2 \* (rho_liquid - rho_gas) \* g) / (9 \* v_terminal)



3\. Convert the bubble radius from centimetres to metres.



4\. Convert the terminal velocity from centimetres per second to metres per second.



5\. Use 1440 kg/m³ as the single experimentally measured glycerol density. Clearly label its source and do not invent an uncertainty.



6\. Calculate viscosity in Pa·s.



7\. Print all input quantities with their corresponding SI units.



8\. Print the resulting dynamic viscosity with units of Pa·s.



9\. Independently check that the numerical calculation gives approximately 0.82 Pa·s.



10\. Save a CSV file named glycerol_viscosity_result.csv containing the input quantities, units and calculated viscosity.



11\. Save a short text file named glycerol_viscosity_calculation.txt documenting the Stokes equation, numerical substitutions, unit conversions and assumptions.



12\. If possible, compare the calibration factors implied by the saved bubble radius and terminal velocity with the reference factor 14.3 / 852.78 cm/pixel. Flag any discrepancy without silently changing the measurements.



13\. Label the calculated viscosity as provisional because the calibration consistency, full uncertainty propagation and validity of the Stokes approximation still need to be assessed.



14\. Do not calculate uncertainty propagation yet. That will be done in the next phase.



15\. Do not modify any existing tracking, calibration, radius, velocity or density files.

---

**## Prompt 19 — Glycerol Calibration Consistency**

Create a new Python script called glycerol_calibration_consistency.py for Laboratory 1 – Viscosity.



We have already analyzed the glycerol bubble video, calculated its velocity, measured its radius, and obtained a provisional viscosity.



However, we found a small discrepancy between the calibration factors used in the calculations.



The reference calibration measurements are:

\- Real distance: 14.3 cm

\- Pixel distance: 852.78 pixels

\- Reference calibration factor: 14.3 / 852.78 cm/pixel



Please:



1\. Load the original measurements from glycerol_tracking_every10frames.csv and glycerol_radius_multiple.csv.

2\. Check the actual CSV column names before processing the data.

3\. Recalculate the bubble's upward positions using the reference calibration factor.

4\. Recalculate the interval velocities using the original timestamps.

5\. Calculate the mean velocity and sample standard deviation of the first six intervals.

6\. Recalculate the individual bubble radii from their original pixel diameters using the same reference calibration factor.

7\. Calculate the mean bubble radius and sample standard deviation using the six valid radius measurements.

8\. Convert all quantities into SI units.

9\. Calculate glycerol viscosity using Stokes' law:



mu = 2 \* R\*\*2 \* (rho_liquid - rho_air) \* g / (9 \* v_terminal)



Use:

\- Glycerol density = 1440 kg/m³ (one real experimental measurement)

\- Air density = 1.2 kg/m³ (assumed)

\- Gravity = 9.81 m/s²



10\. Compare the recalculated results with our previous results:

\- Mean radius = 0.3528 cm

\- Terminal velocity = 4.754 cm/s

\- Provisional viscosity = 0.8212 Pa·s



11\. Print all corrected results in the terminal with their units.

12\. Save the new calculations in glycerol_consistent_results.csv.

13\. Do not overwrite, delete or modify any existing measurement files.

14\. Do not use simulated density measurements as real experimental observations.

15\. Do not calculate uncertainty propagation yet.

---

**## Prompt 20 — Glycerol Uncertainty Propagation**

Create a new Python script called glycerol_uncertainty.py for Laboratory 1 – Viscosity.



We have already calculated the corrected glycerol viscosity using Stokes' law.



The corrected experimental results are stored in glycerol_consistent_results.csv.



I now need to calculate the uncertainty in the glycerol viscosity using error propagation.



Please:



1\. Load glycerol_consistent_results.csv and identify the summary and result rows using the actual column names.



2\. Extract the following corrected quantities:

   - Mean bubble radius (m)

   - Sample standard deviation of bubble radius (m)

   - Mean terminal velocity from the first six intervals (m/s)

   - Sample standard deviation of terminal velocity (m/s)

   - Glycerol density (kg/m³)

   - Air density (kg/m³)

   - Dynamic viscosity (Pa·s)



3\. Verify that the values are approximately:

   - Mean radius = 0.003514669 m

   - Radius standard deviation = 0.000121669 m

   - Terminal velocity = 0.047354922 m/s

   - Velocity standard deviation = 0.000668414 m/s

   - Glycerol density = 1440 kg/m³

   - Air density = 1.2 kg/m³

   - Viscosity = 0.818202 Pa·s



4\. Calculate the partial propagated uncertainty using:



   sigma_mu_partial = mu \* sqrt(

       (2 \* sigma_R / R)\*\*2 +

       (sigma_v / v_terminal)\*\*2

   )



5\. Calculate and print the relative uncertainty contributions from radius and velocity separately, expressed as percentages.



6\. Calculate the combined partial relative uncertainty in percent.



7\. Report the provisional result as:



   Dynamic viscosity = mu ± sigma_mu_partial (Pa·s)



8\. IMPORTANT: We only have one genuine experimental glycerol density measurement. Do not use the previously simulated density measurements to calculate experimental uncertainty.



9\. Clearly explain in the terminal output that the calculated uncertainty is PARTIAL because it excludes density uncertainty, calibration uncertainty, measurement bias and possible systematic errors.



10\. Also display the complete uncertainty propagation equation including liquid density uncertainty, but do not assign any invented value to that uncertainty.



11\. Save a summary of the calculations in glycerol_uncertainty_results.csv.



12\. Save a short readable explanation in glycerol_uncertainty_report.txt.



13\. Do not overwrite, modify or delete any existing experimental measurements or results.



14\. Do not install additional libraries.



Keep the program simple, scientifically correct and easy to understand.

---

**## Prompt 21 — Unified Video Analysis**

I want to reorganize my Transport Phenomena Laboratory 1 project.



My actual experiment includes THREE different fluids:

\- Water

\- Glycerol

\- Oil



Each fluid has its own experimental video.



IMPORTANT: The glycerol video analyzed so far belongs to the professor. I also have my own glycerol video, which must be analyzed independently for my laboratory report.



My goal is to have ONE reusable Python program that can analyze all three fluids instead of separate hard-coded scripts.



Please first inspect the existing Python scripts and files in my "lab bubbles" project.



I want you to:



1\. Identify which existing scripts handle video loading, manual bubble tracking, spatial calibration, radius measurement, velocity calculation, viscosity calculation, uncertainty propagation, and plotting.

2\. Explain which parts of the code can be reused for all three fluids.

3\. Propose a simple program structure with one main entry point called analyze_bubbles.py.

4\. Allow users to choose a fluid and select the corresponding original video.

5\. Ensure that each video has its own calibration, bubble measurements, density inputs, and terminal-velocity selection.

6\. Save outputs in separate folders for water, glycerol, and oil.

7\. Preserve the professor's glycerol measurements as a separate test dataset.

8\. Avoid duplicated code where possible.

9\. Keep the manual tracking procedure and original frame timestamps.

10\. Do not use simulated measurements as genuine experimental data.



VERY IMPORTANT:

Do not create, modify, delete, or overwrite any files yet.



For now, only inspect the project and explain your proposed structure and the implementation steps.



Keep the solution beginner-friendly and compatible with our existing Python environment.

---

**## Prompt 22 — Unified Bubble Analysis: Video Selection**

We have completed the read-only project inspection.



Now let's start implementing ONE reusable Python program for my Transport Phenomena Laboratory 1.



The program must eventually analyze three different fluids: water, glycerol, and oil, using the same code.



For this first implementation step, create a new file named analyze_bubbles.py.



IMPORTANT: Implement ONLY video selection and video validation for now. Do not implement tracking, calibration, viscosity calculations, or plotting yet.



Requirements:



1\. Display a simple menu allowing me to choose:

   - Water

   - Glycerol

   - Oil



2\. Find available video files in the existing "videos lab transporte" folder and the project directory.



3\. The project currently contains videos named:

   - fluids lab water.mp4

   - fluids lab glycerol.mp4

   - fluids lab oil.mp4



4\. Let the user select and confirm the correct video. Do not assume that a filename proves who recorded the video.



5\. Open the selected original video using OpenCV.



6\. Display:

   - Selected fluid

   - Full video path

   - Video FPS

   - Total number of frames

   - Video width and height

   - Video duration in seconds



7\. Check that the video opens correctly and display a clear error message if it cannot be opened.



8\. Do not hard-code FPS, frame dimensions, crop coordinates, or frame numbers.



9\. Do not resample or convert the original video.



10\. Keep the professor's previous glycerol analysis separate from my own glycerol experiment.



11\. Do not modify, overwrite, move, or delete any existing scripts, videos, CSV files, measurements, or results.



12\. Do not create output folders or experimental result files yet.



13\. Use the existing Python environment and installed libraries.



14\. Keep the code beginner-friendly, readable, and organized into reusable functions so that we can add calibration and tracking in the next steps.



After creating analyze_bubbles.py, explain how to run it from the VS Code terminal.



Do not implement additional features until we have tested this first version.

---

**# Prompt 23 — Windows File Explorer Video Selection**

Modify the existing analyze_bubbles.py script.



I want to select my experimental videos using the Windows File Explorer instead of choosing from a numbered list of video filenames.



Please:



1\. Keep the initial menu where I choose the fluid: Water, Glycerol, or Oil.



2\. After selecting the fluid, automatically open the native Windows file selection dialog using tkinter.filedialog.askopenfilename().



3\. Allow me to browse my entire computer and manually select the video file I want to analyze.



4\. Support common video formats, including .mp4, .MOV, .avi and .mkv.



5\. Do not require videos to be stored inside the project folder.



6\. After selecting a video, display its full file path, FPS, total frame count, width, height and duration using OpenCV.



7\. Ask me to confirm that I selected the correct video before continuing.



8\. If I cancel the file selection window, handle it gracefully without crashing.



9\. Reject the known resampled glycerol_10fps.mp4 file. Analyze original videos only.



10\. Do not hard-code FPS, dimensions, crop coordinates or frame numbers.



11\. Do not modify, overwrite, move or delete any existing videos, experimental measurements or results.



12\. Do not implement calibration, tracking or viscosity calculations yet.



13\. Use tkinter, which is included with standard Python, without installing additional libraries.



Keep the code simple and beginner-friendly.



After modifying the script, explain how I can run it from the VS Code terminal.

---

**## Prompt 24 — Interactive Video Calibration.**

Modify the existing analyze_bubbles.py program to add an interactive spatial calibration step.



This program will be used to analyze three fluids: water, glycerol, and oil, using the same Python code.



The program already allows me to choose a fluid, open the Windows File Explorer, select an original video, and confirm the video.



Please preserve all these existing features.



Now add ONLY the spatial calibration functionality.



Requirements:



1\. After I confirm the selected video, ask me to choose a video time in seconds for calibration.



2\. Extract and display the corresponding original video frame using OpenCV.



3\. Allow me to click TWO points with my mouse on known marks of a physical ruler visible in the video.



4\. Clearly mark the two selected points on the displayed frame.



5\. After selecting the points, ask me to enter the real distance between them in centimeters.



6\. Calculate the Euclidean pixel distance between the two clicked points using their coordinates in the ORIGINAL video frame.



7\. Calculate:

   - centimeters_per_pixel = real_distance_cm / pixel_distance

   - meters_per_pixel = centimeters_per_pixel / 100



8\. Print the pixel distance, real distance, centimeters per pixel, and meters per pixel with units.



9\. Allow me to retry the point selection if I click incorrectly.



10\. Allow me to cancel the calibration safely.



11\. Validate that the real distance is positive, the selected points are different, and the selected video time is within the video duration.



12\. Make the frame display usable for portrait and landscape videos. If you resize the frame for display, correctly transform mouse click coordinates back to ORIGINAL frame coordinates.



13\. Do not assume a fixed FPS, video resolution, ruler length, or calibration factor.



14\. Warn me that the ruler must be approximately in the same physical plane as the bubble's trajectory to avoid perspective-related errors.



15\. Implement the calibration as a reusable function whose returned calibration result can be used later for tracking, velocity, and radius calculations.



16\. Keep the calibration independent for each video. Never reuse the professor's glycerol calibration for my own experiments.



17\. For this implementation stage, just display the calibration result. Do not create or overwrite experimental results files yet.



18\. Do not modify, delete, or overwrite any existing measurement CSV files, videos, or previous results.



19\. Do not implement bubble tracking, radius measurement, viscosity calculations, or uncertainty calculations yet. We will add those later after testing calibration.



20\. Use the existing Python environment and installed libraries. Do not install anything new.



Keep the program beginner-friendly and explain how I should test the calibration step manually.

---

**## Prompt 25 — Save Calibration Results**

Modify the existing analyze_bubbles.py program to save the calibration results for each experiment.



The interactive video selection and spatial calibration are already working correctly. Preserve both features.



Please:



1\. After a successful calibration, create an independent results folder for the selected fluid and experimental run.



2\. Use this structure:

   results/water/run_id/

   results/glycerol/run_id/

   results/oil/run_id/



3\. Create a unique run ID automatically so previous experiments are never overwritten.



4\. Save calibration.json containing:

   - Selected fluid

   - Original video file path

   - Video FPS, frame count and resolution

   - Calibration frame index and timestamp

   - Original pixel coordinates of both selected ruler points

   - Real distance in centimeters

   - Pixel distance

   - Centimeters per pixel

   - Meters per pixel



5\. Save the calibration only after the user successfully completes and confirms it.



6\. Print the path of the saved calibration file in the terminal.



7\. Never overwrite or delete previous experimental results.



8\. Keep the professor's glycerol measurements separate from my own experiments.



9\. Do not modify any existing experimental CSV files or videos.



10\. Do not add bubble tracking or viscosity calculations yet.



11\. Do not install additional libraries.



12\. Keep the code simple and beginner-friendly.



After modifying the script, explain how to test that calibration.json is saved correctly.

---

**## Prompt 26 — Reusable Manual Bubble Tracking.**

Modify the existing analyze_bubbles.py program to add reusable manual bubble tracking for Laboratory 1 – Viscosity.



The program already supports:

\- Choosing Water, Glycerol, or Oil

\- Selecting an original video using Windows File Explorer

\- Reading video metadata

\- Interactive spatial calibration

\- Saving calibration.json in a unique experimental run folder



IMPORTANT: Preserve all existing functionality and previously saved results.



We now need to add manual bubble tracking.



Requirements:



1\. Allow me to continue an existing experimental run by selecting its calibration.json file using the Windows File Explorer.



2\. When loading an existing calibration, read its video path, fluid, FPS, dimensions, and calibration factor. Validate the data and confirm that the original video is available.



3\. Do not make me repeat the calibration if calibration.json already exists.



4\. Keep the option to start a completely new experiment.



5\. Ask me for the start and end times of the video interval I want to analyze, in seconds. Validate that both times are within the video duration and that the end time is later than the start time.



6\. Ask how many ORIGINAL video frames to skip between measurements. Suggest 10 frames by default, but allow a different positive integer.



7\. Use the original video FPS and original frame indices. Never resample the video or assume a fixed FPS.



8\. Show each selected frame in a Matplotlib window and let me manually click the CENTER of the SAME rising bubble.



9\. Clearly display the current frame number and timestamp.



10\. Mark my selected point on the image and allow me to accept, retry, or skip the frame.



11\. Allow me to cancel the tracking process safely.



12\. If the image is resized for display, preserve the original video pixel coordinates.



13\. Do not use fixed crop coordinates or assume a particular image resolution.



14\. For each accepted measurement, record:

    - Original frame index

    - Timestamp in seconds

    - Bubble center x coordinate in original pixels

    - Bubble center y coordinate in original pixels



15\. Use the saved calibration factor to calculate the upward vertical displacement in meters relative to the first accepted tracking point. Image y coordinates increase downward, so upward displacement must be positive when the bubble rises.



16\. After tracking, show a preview of the recorded measurements.



17\. Ask for confirmation before saving.



18\. Save the measurements as bubble_tracking.csv inside the SAME experimental run folder that contains calibration.json.



19\. Never overwrite an existing bubble_tracking.csv or any other experimental measurement file. If tracking already exists, explain this clearly instead of silently replacing it.



20\. Never mix measurements from different videos or fluids.



21\. Keep the professor's glycerol data completely separate from my experimental runs.



22\. Do not implement radius measurement, velocity calculation, viscosity calculation, uncertainty propagation, or plotting yet. We will add those after manually testing the tracking.



23\. Do not install additional libraries.



Keep the code beginner-friendly, with clear instructions in the terminal and reusable functions.



After implementing this stage, explain how to load my existing water calibration.json and track one rising bubble without recalibrating.

---

### Extra prompt — Enlarged view for small bubbles (recovered from conversation)

Modify the existing analyze_bubbles.py to make manual tracking of very small bubbles easier.

In my water experiment, the bubbles are extremely small and difficult to see in the current Matplotlib window.

Please improve ONLY the bubble tracking interface.

Requirements:

1. Keep all existing functionality, including video selection, calibration loading, and saving measurements.
2. Before tracking, allow me to select a rectangular region of interest (ROI) around the bubble's trajectory using the mouse.
3. Display this region enlarged by approximately 3x to 5x so I can clearly identify small bubbles.
4. Allow me to adjust or reselect the region if necessary.
5. Display the original full frame as a reference so I can check which bubble I am following.
6. Let me click the center of the bubble in the enlarged view.
7. IMPORTANT: Convert the selected coordinates back to ORIGINAL full-frame pixel coordinates before saving measurements. Account for the crop origin and display scaling.
8. Keep the original frame indices and timestamps. Do not resample the video.
9. Allow me to accept, retry, skip, or cancel each measurement safely.
10. Let me choose a smaller frame interval, such as 3 or 5 original frames, when needed to follow fast-moving bubbles.
11. Do not apply image processing that could distort the bubble location. Optional display-only contrast enhancement is acceptable, but preserve the original measurements.
12. Do not change or overwrite existing calibration.json or bubble_tracking.csv files.
13. Do not modify any previous experimental results.
14. Do not add velocity, radius, or viscosity calculations yet.
15. Keep the interface beginner-friendly and explain how to use the zoom while tracking.

After implementing, explain how to test the enlarged tracking window using my existing water experiment.

---

### Extra prompt — Repeat bubble tracking without overwriting

Modify the existing analyze_bubbles.py program.



I need to repeat bubble tracking using a DIFFERENT time interval without repeating spatial calibration.



Currently, when I continue an existing run, the program displays:



"This run already contains bubble_tracking.csv. It will not be overwritten. Select a different run or start a new one."



Please improve this behavior.



Requirements:



1\. Allow me to continue an existing experimental run even if bubble_tracking.csv already exists.



2\. When previous tracking measurements exist, offer an option to start a NEW tracking attempt.



3\. Reuse the existing calibration.json and original video. Do not require recalibration.



4\. For every new tracking attempt, allow me to choose:

   - A new start time

   - A new end time

   - A new frame interval (for example, 3, 5, or 10 original frames)



5\. Never overwrite or delete previous measurements.



6\. Save new tracking attempts using unique filenames, such as:

   - bubble_tracking.csv (original attempt)

   - bubble_tracking_attempt_02.csv

   - bubble_tracking_attempt_03.csv



7\. Clearly display which tracking attempt is being created and where it will be saved.



8\. Preserve all existing functionality, including any zoom or region-of-interest functionality already implemented.



9\. Do not modify the original videos, existing calibration files, or previous experimental results.



10\. Do not implement velocity or viscosity calculations yet.



Keep the modification simple and beginner-friendly.



After implementing, explain how I can repeat tracking in my existing Water experiment using a different time interval.

---

### Final integration prompt 

Please stop adding unnecessary features. I need one simple, complete, functional program for analyzing my own experimental videos of WATER, GLYCEROL and OLIVE OIL.

We already have analyze_bubbles.py with working video selection, calibration and manual tracking. We also have existing glycerol scripts for velocity, radius, viscosity and uncertainty calculations.

Please REUSE the existing code and complete the remaining workflow in one focused implementation.

REQUIRED FUNCTIONALITY:

1. Open an original video through Windows File Explorer and select the fluid.
2. Reuse an existing calibration.json without repeating calibration.
3. Allow multiple tracking attempts with different start times, end times and frame intervals, without overwriting previous results.
4. Provide a simple zoom or enlarged region for tracking very small bubbles, always saving original-frame pixel coordinates.
5. Calculate and save position versus time and velocity versus time, with correctly labelled PNG graphs.
6. Allow the user to select the approximately constant-velocity portion of the measurements to estimate terminal velocity. Do not automatically assume the first six intervals are valid.
7. Allow manual measurement of bubble radius on several video frames using the existing calibration.
8. Allow entry of real experimental density measurements. Five genuine physical measurements are required for experimental density standard deviation. Never substitute simulated values or pretend missing measurements exist.
9. Calculate viscosity using the laboratory's approximate Stokes equation, with consistent SI units.
10. Calculate and report uncertainty propagation using the uncertainty data actually available. Clearly label partial uncertainties.
11. Save the final results, measurements, graphs and a summary in the correct experimental run folder.
12. Provide a clear comparison table of density, bubble radius, terminal velocity and viscosity, with units and uncertainties.
13. If measurements are insufficient or unreliable, mark the corresponding quantity as incomplete rather than inventing results.
14. Keep the professor's previous glycerol dataset separate from my experimental results.
15. Preserve all previous scripts, calibration files, videos and experimental measurements. Never overwrite results.
16. Keep the implementation simple and beginner-friendly. Use existing installed libraries.
17. Run non-destructive tests and correct any programming errors you find.
18. Do not create extra features unrelated to Laboratory 1.

After implementation, give me ONE concise set of instructions explaining exactly how to analyze each of my three videos and find the resulting graphs and numerical data.

The goal is to obtain the measurements and figures required for the scientific laboratory report.
