from dataclasses import dataclass
from datetime import datetime
import csv
import json
import math
from pathlib import Path
import statistics
import tkinter as tk
from tkinter import filedialog
from uuid import uuid4

import cv2
import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent
VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv"}
KNOWN_RESAMPLED_VIDEO = PROJECT_DIR / "glycerol_10fps.mp4"
FLUIDS = ("Water", "Glycerol", "Oil")


@dataclass(frozen=True)
class VideoInfo:
    path: Path
    fps: float
    frame_count: int
    width: int
    height: int
    duration_seconds: float


@dataclass(frozen=True)
class SpatialCalibration:
    fluid: str
    video_path: Path
    frame_index: int
    frame_time_seconds: float
    first_point_pixels: tuple
    second_point_pixels: tuple
    pixel_distance: float
    real_distance_cm: float
    centimeters_per_pixel: float
    meters_per_pixel: float


@dataclass(frozen=True)
class ExperimentRun:
    fluid: str
    video_info: VideoInfo
    run_directory: Path
    calibration_path: Path
    centimeters_per_pixel: float
    meters_per_pixel: float


def choose_fluid():
    print("Choose the fluid for this experiment:")
    for number, fluid in enumerate(FLUIDS, start=1):
        label = "Oil (sunflower oil)" if fluid == "Oil" else fluid
        print(f"  {number}. {label}")
    print("  0. Exit")

    while True:
        choice = input("Enter a number: ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(FLUIDS):
            return FLUIDS[int(choice) - 1]
        print("Invalid choice. Select Water, Glycerol, Oil, or 0 to exit.")


def select_video_file():
    root = tk.Tk()
    root.withdraw()
    try:
        selected_path = filedialog.askopenfilename(
            parent=root,
            title="Select the original experiment video",
            filetypes=(
                ("MP4 videos", "*.mp4 *.MP4"),
                ("MOV videos", "*.mov *.MOV"),
                ("AVI videos", "*.avi *.AVI"),
                ("MKV videos", "*.mkv *.MKV"),
                ("Other supported videos", "*.m4v *.M4V *.wmv *.WMV"),
                ("All files", "*.*"),
            ),
        )
    finally:
        root.destroy()

    if not selected_path:
        return None
    return Path(selected_path).expanduser().resolve()


def read_video_info(video_path):
    if not video_path.is_file():
        raise FileNotFoundError(f"The selected file no longer exists: {video_path}")

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise RuntimeError(
                "OpenCV could not open this video. Check that the file is a "
                "supported video and is not damaged."
            )

        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count_value = float(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width_value = float(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height_value = float(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        properties = (fps, frame_count_value, width_value, height_value)
        if not all(math.isfinite(value) for value in properties):
            raise ValueError("The video contains invalid or unavailable metadata.")
        if fps <= 0 or frame_count_value <= 0 or width_value <= 0 or height_value <= 0:
            raise ValueError(
                "The video opened, but its FPS, frame count, or dimensions "
                "could not be read."
            )

        frame_count = round(frame_count_value)
        width = round(width_value)
        height = round(height_value)
        return VideoInfo(
            path=video_path,
            fps=fps,
            frame_count=frame_count,
            width=width,
            height=height,
            duration_seconds=frame_count / fps,
        )
    finally:
        capture.release()


def display_video_info(fluid, info):
    print("\nSelected video details")
    print(f"Selected fluid: {fluid}")
    print(f"Full video path: {info.path}")
    print(f"Video FPS: {info.fps:.6g}")
    print(f"Total number of frames: {info.frame_count}")
    print(f"Video width and height: {info.width} x {info.height} pixels")
    print(f"Video duration: {info.duration_seconds:.3f} seconds")


def choose_calibration_time(info):
    while True:
        entry = input(
            "Enter a calibration frame time in seconds (or q to cancel): "
        ).strip()
        if entry.lower() in ("q", "quit", "cancel"):
            return None

        try:
            requested_time = float(entry)
        except ValueError:
            print("Enter a number of seconds, or q to cancel.")
            continue

        if (
            not math.isfinite(requested_time)
            or requested_time < 0
            or requested_time > info.duration_seconds
        ):
            print(
                f"Enter a finite time from 0 to "
                f"{info.duration_seconds:.3f} seconds."
            )
            continue

        frame_index = min(round(requested_time * info.fps), info.frame_count - 1)
        frame_time = frame_index / info.fps
        print(
            f"Using original frame {frame_index} at "
            f"{frame_time:.6f} seconds (nearest frame to {requested_time:.6f} seconds)."
        )
        return frame_index, frame_time


def read_original_frame(info, frame_index):
    capture = cv2.VideoCapture(str(info.path))
    try:
        if not capture.isOpened():
            raise RuntimeError(f"OpenCV could not reopen the video: {info.path}")
        if not capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index):
            raise RuntimeError(f"Could not seek to original video frame {frame_index}.")

        success, frame = capture.read()
        if not success or frame is None:
            raise RuntimeError(f"Could not read original video frame {frame_index}.")
        return frame
    finally:
        capture.release()


def get_screen_size():
    root = tk.Tk()
    root.withdraw()
    try:
        return root.winfo_screenwidth(), root.winfo_screenheight()
    finally:
        root.destroy()


def figure_size_for_frame(frame, screen_size):
    height, width = frame.shape[:2]
    screen_width, screen_height = screen_size
    dpi = plt.rcParams["figure.dpi"]
    display_scale = min(
        (screen_width * 0.85 / dpi) / width,
        (screen_height * 0.75 / dpi) / height,
    )
    return width * display_scale, height * display_scale


def select_calibration_points(frame):
    height, width = frame.shape[:2]
    figure_size = figure_size_for_frame(frame, get_screen_size())
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    while True:
        points = []
        cancelled = []
        figure, axis = plt.subplots(figsize=figure_size)
        axis.imshow(frame_rgb, aspect="equal")
        axis.set_xlim(-0.5, width - 0.5)
        axis.set_ylim(height - 0.5, -0.5)
        axis.axis("off")
        axis.set_title(
            "Click two ruler marks with the left mouse button. "
            "Press Q or Escape to cancel."
        )

        def on_click(event):
            if (
                event.inaxes is not axis
                or event.button != 1
                or event.xdata is None
                or event.ydata is None
                or len(points) == 2
            ):
                return

            x_pixels = float(event.xdata)
            y_pixels = float(event.ydata)
            if not (0 <= x_pixels < width and 0 <= y_pixels < height):
                return

            points.append((x_pixels, y_pixels))
            color = "yellow" if len(points) == 1 else "cyan"
            axis.scatter(
                x_pixels,
                y_pixels,
                s=110,
                marker="o",
                facecolors="none",
                edgecolors=color,
                linewidths=2.5,
            )
            axis.annotate(
                f"Point {len(points)}",
                (x_pixels, y_pixels),
                xytext=(8, 8),
                textcoords="offset points",
                color=color,
                bbox={"facecolor": "black", "alpha": 0.65, "pad": 2},
            )
            if len(points) == 2:
                axis.set_title(
                    "Two points selected. Close the window to review them."
                )
            figure.canvas.draw_idle()

        def on_key(event):
            if event.key in ("q", "escape"):
                cancelled.append(True)
                plt.close(figure)

        figure.canvas.mpl_connect("button_press_event", on_click)
        figure.canvas.mpl_connect("key_press_event", on_key)
        print(
            "\nClick the two ruler marks in the image. "
            "Close the image window when finished; press Q or Escape to cancel."
        )
        plt.show(block=True)
        plt.close(figure)

        if cancelled:
            return None

        if len(points) == 2:
            prompt = "Use these points? [y=accept, r=retry, q=cancel]: "
        else:
            print(f"Selected {len(points)} point(s); exactly two are required.")
            prompt = "Select again? [r=retry, q=cancel]: "

        while True:
            choice = input(prompt).strip().lower()
            if choice in ("q", "quit", "cancel"):
                return None
            if choice in ("r", "retry"):
                break
            if len(points) == 2 and choice in ("y", "yes"):
                return points
            print("Please choose one of the displayed options.")


def enter_real_distance_cm():
    while True:
        entry = input(
            "Enter the real distance between the marks in cm (or q to cancel): "
        ).strip()
        if entry.lower() in ("q", "quit", "cancel"):
            return None

        try:
            distance_cm = float(entry)
        except ValueError:
            print("Enter a number greater than zero, or q to cancel.")
            continue

        if not math.isfinite(distance_cm) or distance_cm <= 0:
            print("The real distance must be a finite value greater than zero.")
            continue
        return distance_cm


def calibrate_video(fluid, info):
    print(
        "\nCalibration warning: keep the ruler approximately in the same physical "
        "plane as the bubble's trajectory to reduce perspective-related errors."
    )

    time_selection = choose_calibration_time(info)
    if time_selection is None:
        return None
    frame_index, frame_time = time_selection
    frame = read_original_frame(info, frame_index)

    while True:
        points = select_calibration_points(frame)
        if points is None:
            return None

        first_point, second_point = points
        pixel_distance = math.hypot(
            second_point[0] - first_point[0],
            second_point[1] - first_point[1],
        )
        if pixel_distance > 0:
            break
        print("The two selected points are identical. Please select them again.")

    real_distance_cm = enter_real_distance_cm()
    if real_distance_cm is None:
        return None

    centimeters_per_pixel = real_distance_cm / pixel_distance
    meters_per_pixel = centimeters_per_pixel / 100
    return SpatialCalibration(
        fluid=fluid,
        video_path=info.path,
        frame_index=frame_index,
        frame_time_seconds=frame_time,
        first_point_pixels=first_point,
        second_point_pixels=second_point,
        pixel_distance=pixel_distance,
        real_distance_cm=real_distance_cm,
        centimeters_per_pixel=centimeters_per_pixel,
        meters_per_pixel=meters_per_pixel,
    )


def display_calibration(calibration):
    print("\nSpatial calibration")
    print(f"Fluid: {calibration.fluid}")
    print(f"Video: {calibration.video_path}")
    print(
        f"Calibration frame: {calibration.frame_index} "
        f"at {calibration.frame_time_seconds:.6f} s"
    )
    print(f"Pixel distance: {calibration.pixel_distance:.3f} pixels")
    print(f"Real distance: {calibration.real_distance_cm:.6g} cm")
    print(
        f"Calibration factor: "
        f"{calibration.centimeters_per_pixel:.10g} cm/pixel"
    )
    print(f"Calibration factor: {calibration.meters_per_pixel:.10g} m/pixel")


def confirm_calibration_save():
    while True:
        choice = input("Save this calibration? [y/N]: ").strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def create_run_directory(fluid):
    fluid_directory = PROJECT_DIR / "results" / fluid.lower()
    fluid_directory.mkdir(parents=True, exist_ok=True)

    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"{timestamp}_{uuid4().hex[:8]}"
        run_directory = fluid_directory / run_id
        try:
            run_directory.mkdir()
        except FileExistsError:
            continue
        return run_id, run_directory


def save_calibration(calibration, video_info):
    run_id, run_directory = create_run_directory(calibration.fluid)
    calibration_path = run_directory / "calibration.json"
    calibration_data = {
        "run_id": run_id,
        "dataset_role": "user_experiment",
        "selected_fluid": calibration.fluid,
        "original_video_file_path": str(video_info.path),
        "video_fps": video_info.fps,
        "video_frame_count": video_info.frame_count,
        "video_resolution_pixels": {
            "width": video_info.width,
            "height": video_info.height,
        },
        "video_duration_seconds": video_info.duration_seconds,
        "calibration_frame_index": calibration.frame_index,
        "calibration_timestamp_seconds": calibration.frame_time_seconds,
        "first_ruler_point_original_pixels": {
            "x": calibration.first_point_pixels[0],
            "y": calibration.first_point_pixels[1],
        },
        "second_ruler_point_original_pixels": {
            "x": calibration.second_point_pixels[0],
            "y": calibration.second_point_pixels[1],
        },
        "real_distance_cm": calibration.real_distance_cm,
        "pixel_distance_pixels": calibration.pixel_distance,
        "centimeters_per_pixel": calibration.centimeters_per_pixel,
        "meters_per_pixel": calibration.meters_per_pixel,
    }

    with calibration_path.open("x", encoding="utf-8") as output_file:
        json.dump(calibration_data, output_file, indent=2)
        output_file.write("\n")
    return calibration_path


def choose_experiment_mode():
    print("\nChoose how to proceed:")
    print("  1. Start a new experiment")
    print("  2. Continue an existing run from calibration.json")
    print("  0. Exit")

    while True:
        choice = input("Enter a number: ").strip()
        if choice == "0":
            return None
        if choice in ("1", "2"):
            return choice
        print("Invalid choice. Select 1, 2, or 0.")


def select_calibration_file():
    root = tk.Tk()
    root.withdraw()
    try:
        selected_path = filedialog.askopenfilename(
            parent=root,
            title="Select a saved calibration.json",
            filetypes=(
                ("Calibration JSON", "calibration.json"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ),
        )
    finally:
        root.destroy()

    if not selected_path:
        return None
    return Path(selected_path).expanduser().resolve()


def json_number(data, key, positive=False):
    value = data.get(key)
    if isinstance(value, bool):
        raise ValueError(f"Calibration field {key!r} must be a number.")
    try:
        value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Calibration field {key!r} must be a number.") from error
    if not math.isfinite(value) or (positive and value <= 0):
        requirement = "a positive finite number" if positive else "a finite number"
        raise ValueError(f"Calibration field {key!r} must be {requirement}.")
    return value


def json_integer(data, key, positive=False):
    value = json_number(data, key, positive=positive)
    if not value.is_integer():
        raise ValueError(f"Calibration field {key!r} must be a whole number.")
    return int(value)


def calibration_point(data, key, width, height):
    point = data.get(key)
    if not isinstance(point, dict):
        raise ValueError(f"Calibration field {key!r} must contain x and y values.")
    x = json_number(point, "x")
    y = json_number(point, "y")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Calibration point {key!r} is outside the video frame.")
    return x, y


def load_existing_run(calibration_path, selected_fluid):
    if calibration_path.name.casefold() != "calibration.json":
        raise ValueError("Select the run's calibration.json file.")
    with calibration_path.open(encoding="utf-8") as calibration_file:
        data = json.load(calibration_file)
    if not isinstance(data, dict):
        raise ValueError("The calibration file must contain a JSON object.")

    if data.get("dataset_role") != "user_experiment":
        raise ValueError(
            "This is not a user experiment calibration. Professor/test glycerol "
            "data cannot be loaded as an experimental run."
        )
    fluid = data.get("selected_fluid")
    if not isinstance(fluid, str) or fluid.casefold() != selected_fluid.casefold():
        raise ValueError(
            f"This calibration is not for the selected fluid ({selected_fluid})."
        )

    expected_fluid_directory = (
        PROJECT_DIR / "results" / selected_fluid.lower()
    ).resolve()
    if calibration_path.parent.parent.resolve() != expected_fluid_directory:
        raise ValueError(
            "The calibration must be inside this project's "
            f"results/{selected_fluid.lower()}/<run_id>/ folder."
        )
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or run_id != calibration_path.parent.name:
        raise ValueError("The run ID in calibration.json does not match its folder.")

    video_path_value = data.get("original_video_file_path")
    if not isinstance(video_path_value, str) or not video_path_value.strip():
        raise ValueError("The calibration does not contain an original video path.")
    video_path = Path(video_path_value).expanduser()
    if not video_path.is_absolute():
        raise ValueError("The saved video path must be an absolute path.")
    video_info = read_video_info(video_path.resolve())

    saved_fps = json_number(data, "video_fps", positive=True)
    saved_frame_count = json_integer(data, "video_frame_count", positive=True)
    resolution = data.get("video_resolution_pixels")
    if not isinstance(resolution, dict):
        raise ValueError("The calibration does not contain video dimensions.")
    saved_width = json_integer(resolution, "width", positive=True)
    saved_height = json_integer(resolution, "height", positive=True)
    if not math.isclose(saved_fps, video_info.fps, rel_tol=1e-6, abs_tol=1e-6):
        raise ValueError("The saved FPS does not match the selected original video.")
    if (saved_frame_count, saved_width, saved_height) != (
        video_info.frame_count,
        video_info.width,
        video_info.height,
    ):
        raise ValueError(
            "The saved frame count or dimensions do not match the original video."
        )

    centimeters_per_pixel = json_number(
        data, "centimeters_per_pixel", positive=True
    )
    meters_per_pixel = json_number(data, "meters_per_pixel", positive=True)
    real_distance_cm = json_number(data, "real_distance_cm", positive=True)
    saved_pixel_distance = json_number(data, "pixel_distance_pixels", positive=True)
    first_point = calibration_point(
        data,
        "first_ruler_point_original_pixels",
        video_info.width,
        video_info.height,
    )
    second_point = calibration_point(
        data,
        "second_ruler_point_original_pixels",
        video_info.width,
        video_info.height,
    )
    measured_pixel_distance = math.hypot(
        second_point[0] - first_point[0],
        second_point[1] - first_point[1],
    )
    if not math.isclose(
        saved_pixel_distance, measured_pixel_distance, rel_tol=1e-6, abs_tol=1e-6
    ):
        raise ValueError("The saved pixel distance does not match the ruler points.")
    if not math.isclose(
        centimeters_per_pixel,
        real_distance_cm / measured_pixel_distance,
        rel_tol=1e-6,
        abs_tol=1e-12,
    ):
        raise ValueError("The saved centimeters-per-pixel factor is inconsistent.")
    if not math.isclose(
        meters_per_pixel,
        centimeters_per_pixel / 100,
        rel_tol=1e-6,
        abs_tol=1e-12,
    ):
        raise ValueError("The saved meters-per-pixel factor is inconsistent.")

    frame_index = json_integer(data, "calibration_frame_index")
    if not 0 <= frame_index < video_info.frame_count:
        raise ValueError("The calibration frame index is outside the original video.")
    frame_time = json_number(data, "calibration_timestamp_seconds")
    if frame_time < 0 or not math.isclose(
        frame_time, frame_index / video_info.fps, rel_tol=1e-6, abs_tol=1e-6
    ):
        raise ValueError("The saved calibration timestamp is inconsistent.")

    return ExperimentRun(
        fluid=selected_fluid,
        video_info=video_info,
        run_directory=calibration_path.parent,
        calibration_path=calibration_path,
        centimeters_per_pixel=centimeters_per_pixel,
        meters_per_pixel=meters_per_pixel,
    )


def start_new_experiment(fluid):
    while True:
        try:
            video_path = select_video_file()
        except tk.TclError as error:
            print(f"\nError opening the Windows file-selection dialog: {error}")
            return None

        if video_path is None:
            print("Video selection cancelled.")
            return None

        print(f"\nSelected fluid: {fluid}")
        print(f"Full video path: {video_path}")
        if fluid == "Glycerol":
            print(
                "Confirm this is your own glycerol video; the professor's previous "
                "glycerol measurements are not loaded or changed."
            )
        if video_path == KNOWN_RESAMPLED_VIDEO.resolve():
            print(
                "Error: This known glycerol video was resampled to 10 FPS. "
                "Select an original video instead."
            )
            continue
        if video_path.suffix.lower() not in VIDEO_SUFFIXES:
            print(
                "Error: Select a supported video file "
                "(.mp4, .MOV, .avi, .mkv, .m4v, or .wmv)."
            )
            continue

        try:
            video_info = read_video_info(video_path)
        except (FileNotFoundError, RuntimeError, ValueError, cv2.error) as error:
            print(f"\nError validating the selected video: {error}")
            continue

        display_video_info(fluid, video_info)
        while True:
            confirmation = input(
                "Confirm this is the correct original video for this "
                "experiment? [y/N]: "
            ).strip().lower()
            if confirmation in ("y", "yes"):
                print("Video confirmed.")
                break
            if confirmation in ("", "n", "no"):
                print("Please select the correct video.")
                break
            print("Please answer y or n.")

        if confirmation in ("", "n", "no"):
            continue

        try:
            calibration = calibrate_video(fluid, video_info)
        except (RuntimeError, ValueError, cv2.error, tk.TclError) as error:
            print(f"\nError during spatial calibration: {error}")
            return None
        if calibration is None:
            print("Spatial calibration cancelled.")
            return None

        display_calibration(calibration)
        if not confirm_calibration_save():
            print("Calibration was not saved.")
            return None

        try:
            calibration_path = save_calibration(calibration, video_info)
        except OSError as error:
            print(f"\nError saving calibration: {error}")
            return None
        print(f"Calibration saved to: {calibration_path}")
        return ExperimentRun(
            fluid=fluid,
            video_info=video_info,
            run_directory=calibration_path.parent,
            calibration_path=calibration_path,
            centimeters_per_pixel=calibration.centimeters_per_pixel,
            meters_per_pixel=calibration.meters_per_pixel,
        )


def continue_existing_experiment(fluid):
    while True:
        try:
            calibration_path = select_calibration_file()
        except tk.TclError as error:
            print(f"\nError opening the calibration file dialog: {error}")
            return None
        if calibration_path is None:
            print("Calibration selection cancelled.")
            return None

        try:
            run = load_existing_run(calibration_path, fluid)
        except (OSError, RuntimeError, ValueError, cv2.error) as error:
            print(f"\nCannot continue from this calibration: {error}")
            continue

        print(f"\nLoaded run ID: {run.run_directory.name}")
        print(f"Calibration file: {run.calibration_path}")
        display_video_info(run.fluid, run.video_info)
        print(
            f"Saved calibration factor: {run.centimeters_per_pixel:.10g} cm/pixel "
            f"({run.meters_per_pixel:.10g} m/pixel)"
        )
        while True:
            confirmation = input(
                "Continue this run with its saved calibration? [y/N]: "
            ).strip().lower()
            if confirmation in ("y", "yes"):
                return run
            if confirmation in ("", "n", "no"):
                print("Select another calibration file or cancel.")
                break
            print("Please answer y or n.")


def existing_tracking_files(run):
    tracking_files = []
    first_attempt = run.run_directory / "bubble_tracking.csv"
    if first_attempt.is_file():
        tracking_files.append(first_attempt)

    attempt_prefix = "bubble_tracking_attempt_"
    for path in run.run_directory.glob(f"{attempt_prefix}*.csv"):
        attempt_number = path.stem[len(attempt_prefix):]
        if path.is_file() and attempt_number.isdigit():
            tracking_files.append(path)

    return tracking_files


def next_tracking_attempt(run, previous_files):
    if not previous_files:
        return 1, run.run_directory / "bubble_tracking.csv"

    highest_attempt = 1 if any(
        path.name == "bubble_tracking.csv" for path in previous_files
    ) else 0
    attempt_prefix = "bubble_tracking_attempt_"
    for path in previous_files:
        if path.stem.startswith(attempt_prefix):
            suffix = path.stem[len(attempt_prefix):]
            if suffix.isdigit():
                highest_attempt = max(highest_attempt, int(suffix))

    attempt_number = max(2, highest_attempt + 1)
    while True:
        tracking_path = run.run_directory / (
            f"{attempt_prefix}{attempt_number:02d}.csv"
        )
        if not tracking_path.exists():
            return attempt_number, tracking_path
        attempt_number += 1


def confirm_new_tracking_attempt(attempt_number, tracking_path):
    while True:
        choice = input(
            f"Start tracking attempt {attempt_number} and save it as "
            f"{tracking_path.name}? [y/N]: "
        ).strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def ask_time(prompt, duration_seconds):
    while True:
        entry = input(f"{prompt} (0 to {duration_seconds:.3f} s, q to cancel): ").strip()
        if entry.lower() in ("q", "quit", "cancel"):
            return None
        try:
            value = float(entry)
        except ValueError:
            print("Enter a time in seconds, or q to cancel.")
            continue
        if not math.isfinite(value) or not 0 <= value <= duration_seconds:
            print(f"Enter a finite time from 0 to {duration_seconds:.3f} seconds.")
            continue
        return value


def choose_tracking_interval(video_info):
    while True:
        start_time = ask_time("Start time", video_info.duration_seconds)
        if start_time is None:
            return None
        end_time = ask_time("End time", video_info.duration_seconds)
        if end_time is None:
            return None
        if end_time <= start_time:
            print("The end time must be later than the start time.")
            continue

        start_frame = min(round(start_time * video_info.fps), video_info.frame_count - 1)
        end_frame = min(round(end_time * video_info.fps), video_info.frame_count - 1)
        if end_frame <= start_frame:
            print("The selected time range must include more than one original frame.")
            continue
        return start_frame, end_frame


def choose_frame_step():
    while True:
        entry = input(
            "Frame interval in ORIGINAL frames [10] "
            "(e.g. 10 means measure every 10 frames; q cancels): "
        ).strip()
        if entry.lower() in ("q", "quit", "cancel"):
            return None
        if not entry:
            return 10
        try:
            step = int(entry)
        except ValueError:
            print("Enter a positive whole number of frames, or q to cancel.")
            continue
        if step <= 0:
            print("The frame interval must be a positive whole number.")
            continue
        return step


def zoom_bounds(frame, point):
    height, width = frame.shape[:2]
    half_size = max(32, min(width, height) // 8)
    center_x = round(point[0])
    center_y = round(point[1])
    left = max(0, center_x - half_size)
    right = min(width, center_x + half_size + 1)
    top = max(0, center_y - half_size)
    bottom = min(height, center_y + half_size + 1)
    return left, top, right, bottom


def select_frame_point(
    frame_rgb, figure_size, title, bounds=None, mark_label=None
):
    height, width = frame_rgb.shape[:2]
    figure, axis = plt.subplots(figsize=figure_size)
    if bounds is None:
        left, top, right, bottom = 0, 0, width, height
        image = frame_rgb
    else:
        left, top, right, bottom = bounds
        image = frame_rgb[top:bottom, left:right]
    axis.imshow(
        image,
        extent=(left - 0.5, right - 0.5, bottom - 0.5, top - 0.5),
        aspect="equal",
    )
    axis.set_xlim(left - 0.5, right - 0.5)
    axis.set_ylim(bottom - 0.5, top - 0.5)
    axis.axis("off")
    axis.set_title(title)
    point = []
    cancelled = []

    def on_click(event):
        if (
            event.inaxes is not axis
            or event.button != 1
            or event.xdata is None
            or event.ydata is None
            or point
        ):
            return
        x_pixels = float(event.xdata)
        y_pixels = float(event.ydata)
        if not (left <= x_pixels < right and top <= y_pixels < bottom):
            return
        point.append((x_pixels, y_pixels))
        axis.scatter(
            x_pixels,
            y_pixels,
            s=110,
            marker="o",
            facecolors="none",
            edgecolors="red",
            linewidths=2.5,
        )
        if mark_label:
            axis.annotate(
                mark_label,
                (x_pixels, y_pixels),
                xytext=(8, 8),
                textcoords="offset points",
                color="red",
                bbox={"facecolor": "white", "alpha": 0.8, "pad": 2},
            )
        axis.set_title("Point marked. Close the window to review.")
        figure.canvas.draw_idle()

    def on_key(event):
        if event.key in ("q", "escape"):
            cancelled.append(True)
            plt.close(figure)

    figure.canvas.mpl_connect("button_press_event", on_click)
    figure.canvas.mpl_connect("key_press_event", on_key)
    plt.show(block=True)
    plt.close(figure)
    if cancelled:
        return "cancel", None
    if point:
        return "selected", point[0]
    return "empty", None


def select_bubble_center(frame, frame_index, timestamp_seconds, screen_size):
    figure_size = figure_size_for_frame(frame, screen_size)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    while True:
        rough_state, rough_point = select_frame_point(
            frame_rgb,
            figure_size,
            f"Original frame {frame_index} | {timestamp_seconds:.6f} s\n"
            "Click near the bubble center; the next view will be enlarged. "
            "Q/Escape cancels.",
        )
        if rough_state == "cancel":
            return "cancel", None
        if rough_state == "empty":
            prompt = "No region selected [r=retry, s=skip, q=cancel]: "
            exact_point = None
        else:
            bounds = zoom_bounds(frame, rough_point)
            left, top, right, bottom = bounds
            print(
                f"Enlarged region: original pixels x={left}..{right - 1}, "
                f"y={top}..{bottom - 1}."
            )
            point_state, exact_point = select_frame_point(
                frame_rgb,
                figure_size,
                f"Frame {frame_index} | {timestamp_seconds:.6f} s\n"
                "Click the exact center of the same rising bubble in this "
                "enlarged region.\n"
                "Coordinates are original-frame pixels; Q/Escape cancels.",
                bounds=bounds,
                mark_label="Bubble center",
            )
            if point_state == "cancel":
                return "cancel", None
            if point_state == "empty":
                exact_point = None
                prompt = "No center selected [r=retry, s=skip, q=cancel]: "
            else:
                prompt = "Frame choice [a=accept, r=retry, s=skip, q=cancel]: "

        while True:
            choice = input(prompt).strip().lower()
            if choice in ("q", "quit", "cancel"):
                return "cancel", None
            if choice in ("r", "retry"):
                break
            if choice in ("s", "skip"):
                return "skip", None
            if exact_point is not None and choice in ("a", "accept"):
                return "accept", exact_point
            print("Please choose one of the displayed options.")


def track_bubble(run, tracking_path):
    if tracking_path.exists():
        raise FileExistsError(
            f"{tracking_path} already exists; tracking data will not be overwritten."
        )

    interval = choose_tracking_interval(run.video_info)
    if interval is None:
        return None
    frame_step = choose_frame_step()
    if frame_step is None:
        return None

    start_frame, end_frame = interval
    frame_indices = range(start_frame, end_frame + 1, frame_step)
    print(
        f"\nTracking {len(frame_indices)} original frame(s), from frame "
        f"{start_frame} through {end_frame}, using a {frame_step}-frame interval."
    )

    capture = cv2.VideoCapture(str(run.video_info.path))
    try:
        if not capture.isOpened():
            raise RuntimeError(
                f"OpenCV could not reopen the original video: {run.video_info.path}"
            )

        screen_size = get_screen_size()
        measurements = []
        first_accepted_y = None
        for frame_index in frame_indices:
            if not capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index):
                raise RuntimeError(f"Could not seek to original frame {frame_index}.")
            success, frame = capture.read()
            if not success or frame is None:
                raise RuntimeError(f"Could not read original frame {frame_index}.")
            if frame.shape[1] != run.video_info.width or frame.shape[0] != run.video_info.height:
                raise RuntimeError(
                    "The original video dimensions changed since calibration."
                )

            timestamp_seconds = frame_index / run.video_info.fps
            print(
                f"\nTracking original frame {frame_index} "
                f"at {timestamp_seconds:.6f} seconds. Click the same rising bubble."
            )
            choice, center = select_bubble_center(
                frame, frame_index, timestamp_seconds, screen_size
            )
            if choice == "cancel":
                return None
            if choice == "skip":
                continue

            center_x, center_y = center
            if first_accepted_y is None:
                first_accepted_y = center_y
            upward_displacement_m = (
                first_accepted_y - center_y
            ) * run.meters_per_pixel
            measurements.append(
                {
                    "frame_index": frame_index,
                    "timestamp_seconds": timestamp_seconds,
                    "bubble_center_x_pixels": center_x,
                    "bubble_center_y_pixels": center_y,
                    "upward_displacement_m": upward_displacement_m,
                }
            )
        return measurements
    finally:
        capture.release()


def preview_tracking(measurements):
    print("\nTracking preview")
    print(
        "Frame | Timestamp (s) | Center X (pixels) | Center Y (pixels) | "
        "Upward displacement (m)"
    )
    for row in measurements:
        print(
            f"{row['frame_index']:5d} | {row['timestamp_seconds']:13.6f} | "
            f"{row['bubble_center_x_pixels']:16.2f} | "
            f"{row['bubble_center_y_pixels']:16.2f} | "
            f"{row['upward_displacement_m']:23.8f}"
        )


def confirm_tracking_save(measurement_count, tracking_path):
    while True:
        choice = input(
            f"Save these {measurement_count} measurements to {tracking_path}? "
            "[y/N]: "
        ).strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def save_tracking(measurements, tracking_path):
    fieldnames = (
        "frame_index",
        "timestamp_seconds",
        "bubble_center_x_pixels",
        "bubble_center_y_pixels",
        "upward_displacement_m",
    )
    with tracking_path.open("x", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(measurements)
    return tracking_path


def choose_radius_measurement_count():
    while True:
        entry = input(
            "How many video frames will you measure for bubble radius? "
            "[3; enter 0 to skip]: "
        ).strip()
        if not entry:
            return 3
        if entry.lower() in ("q", "quit", "cancel"):
            return 0
        try:
            count = int(entry)
        except ValueError:
            print("Enter a non-negative whole number.")
            continue
        if count >= 0:
            return count
        print("Enter a non-negative whole number.")


def select_radius_points(frame, frame_index, timestamp_seconds, screen_size):
    figure_size = figure_size_for_frame(frame, screen_size)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    labels = ("Left edge", "Right edge", "Top edge", "Bottom edge")

    while True:
        rough_state, rough_point = select_frame_point(
            frame_rgb,
            figure_size,
            f"Original frame {frame_index} | {timestamp_seconds:.6f} s\n"
            "Click near the bubble to open an enlarged region. Q/Escape cancels.",
        )
        if rough_state == "cancel":
            return "cancel", None
        if rough_state == "empty":
            choice = input(
                "No region selected [r=retry, s=skip, q=cancel]: "
            ).strip().lower()
            if choice in ("q", "quit", "cancel"):
                return "cancel", None
            if choice in ("s", "skip"):
                return "skip", None
            continue

        left, top, right, bottom = zoom_bounds(frame, rough_point)
        points = []
        figure, axis = plt.subplots(figsize=figure_size)
        axis.imshow(
            frame_rgb[top:bottom, left:right],
            extent=(left - 0.5, right - 0.5, bottom - 0.5, top - 0.5),
            aspect="equal",
        )
        axis.set_xlim(left - 0.5, right - 0.5)
        axis.set_ylim(bottom - 0.5, top - 0.5)
        axis.axis("off")
        plt.show(block=False)

        for index, label in enumerate(labels):
            axis.set_title(
                f"Frame {frame_index} | {timestamp_seconds:.6f} s | "
                f"click {label} ({index + 1}/4)\n"
                "This is enlarged; coordinates remain original-frame pixels."
            )
            figure.canvas.draw_idle()
            clicks = plt.ginput(1, timeout=-1)
            if not clicks or clicks[0][0] is None or clicks[0][1] is None:
                break

            x_pixels, y_pixels = clicks[0]
            if not (
                left <= x_pixels < right
                and top <= y_pixels < bottom
            ):
                break
            points.append((float(x_pixels), float(y_pixels)))
            axis.scatter(
                x_pixels,
                y_pixels,
                s=85,
                color="red",
                edgecolors="white",
                linewidths=1.5,
            )
            axis.annotate(
                label,
                (x_pixels, y_pixels),
                xytext=(5, 5),
                textcoords="offset points",
                color="red",
            )
            figure.canvas.draw_idle()

        valid = len(points) == 4
        if valid:
            left, right, top, bottom = points
            valid = left[0] < right[0] and top[1] < bottom[1]
        if valid:
            horizontal = right[0] - left[0]
            vertical = bottom[1] - top[1]
            axis.plot(
                [left[0], right[0]],
                [(left[1] + right[1]) / 2] * 2,
                color="yellow",
                linewidth=2,
            )
            axis.plot(
                [(top[0] + bottom[0]) / 2] * 2,
                [top[1], bottom[1]],
                color="cyan",
                linewidth=2,
            )
            axis.set_title(
                f"Horizontal diameter: {horizontal:.2f} px; "
                f"vertical diameter: {vertical:.2f} px\n"
                "Close the window to accept, retry, skip, or cancel."
            )
        else:
            axis.set_title(
                "Incomplete or out-of-order points. Close the window to retry, "
                "skip, or cancel."
            )

        plt.show(block=True)
        plt.close(figure)
        if valid:
            prompt = "Radius choice [a=accept, r=retry, s=skip, q=cancel]: "
        else:
            prompt = "Radius choice [r=retry, s=skip, q=cancel]: "

        while True:
            choice = input(prompt).strip().lower()
            if choice in ("q", "quit", "cancel"):
                return "cancel", None
            if choice in ("r", "retry"):
                break
            if choice in ("s", "skip"):
                return "skip", None
            if valid and choice in ("a", "accept"):
                return "accept", points
            print("Please choose one of the displayed options.")


def collect_radius_measurements(run):
    count = choose_radius_measurement_count()
    measurements = []
    if count == 0:
        print("No radius frames selected; radius will be marked incomplete.")
        return measurements

    screen_size = get_screen_size()
    used_frame_indices = set()
    for measurement_number in range(1, count + 1):
        while True:
            selected_time = ask_time(
                f"Time for radius measurement {measurement_number} of {count}",
                run.video_info.duration_seconds,
            )
            if selected_time is None:
                print("Radius-frame selection ended.")
                return measurements

            frame_index = min(
                round(selected_time * run.video_info.fps),
                run.video_info.frame_count - 1,
            )
            if frame_index in used_frame_indices:
                print("Choose a different original video frame for each radius.")
                continue
            used_frame_indices.add(frame_index)
            timestamp_seconds = frame_index / run.video_info.fps
            break

        frame = read_original_frame(run.video_info, frame_index)
        print(
            f"\nMeasure one bubble in original frame {frame_index} "
            f"at {timestamp_seconds:.6f} s."
        )
        choice, points = select_radius_points(
            frame, frame_index, timestamp_seconds, screen_size
        )
        if choice == "cancel":
            print("Radius measurement cancelled.")
            return measurements
        if choice == "skip":
            print(f"Skipped radius measurement at frame {frame_index}.")
            continue

        left, right, top, bottom = points
        horizontal_diameter = right[0] - left[0]
        vertical_diameter = bottom[1] - top[1]
        if horizontal_diameter <= 0 or vertical_diameter <= 0:
            print("The measured diameters must be positive; this frame was skipped.")
            continue

        radius_pixels = math.sqrt(horizontal_diameter * vertical_diameter) / 2
        radius_m = radius_pixels * run.meters_per_pixel
        diameter_ratio = max(horizontal_diameter, vertical_diameter) / min(
            horizontal_diameter, vertical_diameter
        )
        strongly_non_circular = diameter_ratio > 1.20
        if strongly_non_circular:
            print(
                f"WARNING: Diameter ratio {diameter_ratio:.3f} exceeds 1.20. "
                "The measurement is retained but flagged for review."
            )

        measurements.append(
            {
                "frame_index": frame_index,
                "time_seconds": timestamp_seconds,
                "left_x_pixels": left[0],
                "left_y_pixels": left[1],
                "right_x_pixels": right[0],
                "right_y_pixels": right[1],
                "top_x_pixels": top[0],
                "top_y_pixels": top[1],
                "bottom_x_pixels": bottom[0],
                "bottom_y_pixels": bottom[1],
                "horizontal_diameter_pixels": horizontal_diameter,
                "vertical_diameter_pixels": vertical_diameter,
                "radius_pixels": radius_pixels,
                "radius_m": radius_m,
                "horizontal_to_vertical_ratio": diameter_ratio,
                "strongly_non_circular": strongly_non_circular,
            }
        )
        print(f"Measured equivalent radius: {radius_m:.8g} m")

    return measurements


def collect_density_measurements():
    print(
        "\nEnter only density measurements you physically made for this fluid "
        "in kg/m^3. Do not enter simulated or professor/test data."
    )
    while True:
        entry = input(
            "Number of genuine density measurements available "
            "(5 or more are needed for experimental standard deviation; "
            "0 if none): "
        ).strip()
        try:
            count = int(entry)
        except ValueError:
            print("Enter a non-negative whole number.")
            continue
        if count >= 0:
            break
        print("Enter a non-negative whole number.")

    densities = []
    for index in range(1, count + 1):
        while True:
            entry = input(
                f"Density measurement {index} of {count} (kg/m^3): "
            ).strip()
            try:
                density = float(entry)
            except ValueError:
                print("Enter a number greater than zero.")
                continue
            if math.isfinite(density) and density > 0:
                densities.append(density)
                break
            print("Density must be a positive finite number.")
    return densities


def calculate_position_velocity(measurements):
    positions = []
    for row in measurements:
        time_seconds = float(row["timestamp_seconds"])
        frame_index = int(row["frame_index"])
        x_pixels = float(row["bubble_center_x_pixels"])
        y_pixels = float(row["bubble_center_y_pixels"])
        upward_displacement_m = float(row["upward_displacement_m"])
        values = (time_seconds, x_pixels, y_pixels, upward_displacement_m)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Tracking contains a non-finite value.")
        positions.append(
            {
                "frame_index": frame_index,
                "time_seconds": time_seconds,
                "bubble_center_x_pixels": x_pixels,
                "bubble_center_y_pixels": y_pixels,
                "upward_displacement_m": upward_displacement_m,
            }
        )

    if any(
        positions[index + 1]["time_seconds"] <= positions[index]["time_seconds"]
        for index in range(len(positions) - 1)
    ):
        raise ValueError("Tracking timestamps must increase.")

    intervals = []
    for index in range(len(positions) - 1):
        first = positions[index]
        second = positions[index + 1]
        elapsed_seconds = second["time_seconds"] - first["time_seconds"]
        displacement_m = (
            second["upward_displacement_m"] - first["upward_displacement_m"]
        )
        intervals.append(
            {
                "interval_number": index + 1,
                "start_frame_index": first["frame_index"],
                "end_frame_index": second["frame_index"],
                "midpoint_time_seconds": (
                    first["time_seconds"] + second["time_seconds"]
                )
                / 2,
                "displacement_m": displacement_m,
                "time_interval_seconds": elapsed_seconds,
                "velocity_m_s": displacement_m / elapsed_seconds,
                "selected_for_terminal_velocity": False,
            }
        )
    return positions, intervals


def show_velocity_plot(intervals):
    figure, axis = plt.subplots()
    times = [row["midpoint_time_seconds"] for row in intervals]
    velocities = [row["velocity_m_s"] for row in intervals]
    if intervals:
        axis.plot(times, velocities, marker="o", linestyle="-")
    else:
        axis.text(
            0.5,
            0.5,
            "Insufficient position measurements for interval velocity",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
    axis.set_xlabel("Midpoint time (s)")
    axis.set_ylabel("Upward velocity (m/s)")
    axis.set_title("Bubble upward velocity vs. time")
    axis.grid(True)
    figure.tight_layout()
    plt.show()
    plt.close(figure)


def choose_terminal_velocity(intervals):
    if len(intervals) < 2:
        print(
            "\nTerminal velocity is INCOMPLETE: at least two interval "
            "velocities are required to estimate a sample standard deviation."
        )
        return None

    print("\nVelocity intervals (choose a contiguous, approximately constant range):")
    print("No interval is automatically treated as terminal.")
    for row in intervals:
        print(
            f"  {row['interval_number']:3d}: "
            f"midpoint {row['midpoint_time_seconds']:.6f} s, "
            f"velocity {row['velocity_m_s']:.8g} m/s"
        )

    while True:
        try:
            start_entry = input(
                "First interval number in the terminal-velocity range (q cancels): "
            ).strip()
            if start_entry.lower() in ("q", "quit", "cancel"):
                return None
            start_number = int(start_entry)
            end_entry = input("Last interval number in the range: ").strip()
            if end_entry.lower() in ("q", "quit", "cancel"):
                return None
            end_number = int(end_entry)
        except ValueError:
            print("Enter whole interval numbers, or q to mark terminal velocity incomplete.")
            continue

        if not (1 <= start_number <= end_number <= len(intervals)):
            print(f"Choose interval numbers from 1 to {len(intervals)} in order.")
            continue
        selected = intervals[start_number - 1:end_number]
        if len(selected) < 2:
            print("Select at least two consecutive intervals.")
            continue
        if any(row["velocity_m_s"] <= 0 for row in selected):
            print("The selected velocities must all be positive for upward motion.")
            continue

        mean_velocity = statistics.mean(row["velocity_m_s"] for row in selected)
        velocity_deviation = statistics.stdev(
            row["velocity_m_s"] for row in selected
        )
        coefficient_of_variation = velocity_deviation / mean_velocity * 100
        print(
            f"Selected mean velocity: {mean_velocity:.8g} m/s; "
            f"sample standard deviation: {velocity_deviation:.8g} m/s; "
            f"coefficient of variation: {coefficient_of_variation:.3f}%."
        )
        choice = input(
            "Does this selected range look approximately constant on the graph? "
            "[y=accept, r=reselect, q=mark incomplete]: "
        ).strip().lower()
        if choice in ("y", "yes"):
            for row in selected:
                row["selected_for_terminal_velocity"] = True
            return {
                "start_interval_number": start_number,
                "end_interval_number": end_number,
                "mean_velocity_m_s": mean_velocity,
                "sample_standard_deviation_m_s": velocity_deviation,
                "coefficient_of_variation_percent": coefficient_of_variation,
            }
        if choice in ("q", "quit", "cancel"):
            return None
        if choice not in ("r", "reselect"):
            print("Please answer y, r, or q.")


def calculate_lab_results(radius_measurements, density_measurements, terminal):
    radii = [row["radius_m"] for row in radius_measurements]
    mean_radius = statistics.mean(radii) if radii else None
    radius_deviation = statistics.stdev(radii) if len(radii) >= 2 else None
    mean_density = (
        statistics.mean(density_measurements) if density_measurements else None
    )
    density_deviation = (
        statistics.stdev(density_measurements)
        if len(density_measurements) >= 5
        else None
    )

    viscosity = None
    viscosity_uncertainty = None
    uncertainty_terms = []
    if (
        mean_radius is not None
        and terminal is not None
        and mean_density is not None
        and mean_radius > 0
        and terminal["mean_velocity_m_s"] > 0
        and mean_density > 1.2
    ):
        air_density = 1.2
        gravity = 9.81
        density_difference = mean_density - air_density
        velocity = terminal["mean_velocity_m_s"]
        viscosity = (
            2 * mean_radius**2 * density_difference * gravity / (9 * velocity)
        )

        if radius_deviation is not None:
            uncertainty_terms.append((2 * radius_deviation / mean_radius) ** 2)
        if density_deviation is not None:
            uncertainty_terms.append((density_deviation / density_difference) ** 2)
        if terminal["sample_standard_deviation_m_s"] is not None:
            uncertainty_terms.append(
                (terminal["sample_standard_deviation_m_s"] / velocity) ** 2
            )
        if len(uncertainty_terms) == 3:
            viscosity_uncertainty = viscosity * math.sqrt(sum(uncertainty_terms))
        elif len(uncertainty_terms) == 2 and density_deviation is None:
            viscosity_uncertainty = viscosity * math.sqrt(sum(uncertainty_terms))

    radius_reliable = (
        len(radii) >= 3
        and not any(row["strongly_non_circular"] for row in radius_measurements)
    )
    density_reliable = len(density_measurements) >= 5
    viscosity_complete = (
        viscosity is not None
        and viscosity_uncertainty is not None
        and radius_reliable
        and density_reliable
        and terminal is not None
    )
    return {
        "mean_radius_m": mean_radius,
        "radius_sample_standard_deviation_m": radius_deviation,
        "radius_count": len(radii),
        "radius_reliable": radius_reliable,
        "mean_density_kg_m3": mean_density,
        "density_sample_standard_deviation_kg_m3": density_deviation,
        "density_count": len(density_measurements),
        "density_reliable": density_reliable,
        "terminal_velocity_m_s": (
            terminal["mean_velocity_m_s"] if terminal is not None else None
        ),
        "velocity_sample_standard_deviation_m_s": (
            terminal["sample_standard_deviation_m_s"]
            if terminal is not None
            else None
        ),
        "terminal_interval_range": (
            (
                terminal["start_interval_number"],
                terminal["end_interval_number"],
            )
            if terminal is not None
            else None
        ),
        "viscosity_pa_s": viscosity,
        "viscosity_partial_uncertainty_pa_s": viscosity_uncertainty,
        "viscosity_complete": viscosity_complete,
    }


def result_table_rows(results):
    rows = []
    density_status = (
        f"COMPLETE (n={results['density_count']})"
        if results["density_reliable"]
        else f"INCOMPLETE (need 5 genuine readings; n={results['density_count']})"
    )
    radius_status = (
        "COMPLETE"
        if results["radius_reliable"]
        else f"INCOMPLETE (need 3 circular measurements; n={results['radius_count']})"
    )
    if results["radius_count"] and not results["radius_reliable"] and any(
        row["strongly_non_circular"] for row in results.get("radius_measurements", [])
    ):
        radius_status = "INCOMPLETE (one or more measurements are strongly non-circular)"

    if results["terminal_velocity_m_s"] is None:
        velocity_status = "INCOMPLETE (no confirmed constant-velocity range)"
    else:
        velocity_status = "COMPLETE (user-selected range)"

    if results["viscosity_pa_s"] is None:
        viscosity_status = "INCOMPLETE (required mean inputs unavailable)"
    elif results["viscosity_complete"]:
        viscosity_status = "PROVISIONAL (partial uncertainty; systematic effects excluded)"
    else:
        viscosity_status = "INCOMPLETE (data or uncertainty requirements not met)"

    def add_row(quantity, value, uncertainty, unit, status):
        rows.append(
            {
                "quantity": quantity,
                "value": "N/A" if value is None else f"{value:.10g}",
                "uncertainty": (
                    "N/A" if uncertainty is None else f"{uncertainty:.10g}"
                ),
                "unit": unit,
                "status": status,
            }
        )

    add_row(
        "Liquid density",
        results["mean_density_kg_m3"],
        results["density_sample_standard_deviation_kg_m3"],
        "kg/m^3",
        density_status,
    )
    add_row(
        "Bubble radius",
        results["mean_radius_m"],
        results["radius_sample_standard_deviation_m"],
        "m",
        radius_status,
    )
    add_row(
        "Terminal velocity",
        results["terminal_velocity_m_s"],
        results["velocity_sample_standard_deviation_m_s"],
        "m/s",
        velocity_status,
    )
    add_row(
        "Dynamic viscosity",
        results["viscosity_pa_s"],
        results["viscosity_partial_uncertainty_pa_s"],
        "Pa*s",
        viscosity_status,
    )
    return rows


def print_result_table(rows):
    print("\nLaboratory 1 comparison table")
    print(
        f"{'Quantity':<22} {'Value':>16} {'Uncertainty':>16} "
        f"{'Unit':<8} Status"
    )
    for row in rows:
        print(
            f"{row['quantity']:<22} {row['value']:>16} "
            f"{row['uncertainty']:>16} {row['unit']:<8} {row['status']}"
        )


def create_analysis_directory(run):
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = run.run_directory / (
            f"analysis_{timestamp}_{uuid4().hex[:8]}"
        )
        try:
            directory.mkdir()
            return directory
        except FileExistsError:
            continue


def save_analysis_results(
    run,
    tracking_path,
    positions,
    intervals,
    radius_measurements,
    density_measurements,
    terminal,
    results,
):
    analysis_directory = create_analysis_directory(run)
    table_rows = result_table_rows(
        {**results, "radius_measurements": radius_measurements}
    )

    with (analysis_directory / "position_vs_time.csv").open(
        "x", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(positions[0]))
        writer.writeheader()
        writer.writerows(positions)

    velocity_fields = (
        "interval_number",
        "start_frame_index",
        "end_frame_index",
        "midpoint_time_seconds",
        "displacement_m",
        "time_interval_seconds",
        "velocity_m_s",
        "selected_for_terminal_velocity",
    )
    with (analysis_directory / "velocity_vs_time.csv").open(
        "x", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=velocity_fields)
        writer.writeheader()
        writer.writerows(intervals)

    radius_fields = (
        "frame_index",
        "time_seconds",
        "left_x_pixels",
        "left_y_pixels",
        "right_x_pixels",
        "right_y_pixels",
        "top_x_pixels",
        "top_y_pixels",
        "bottom_x_pixels",
        "bottom_y_pixels",
        "horizontal_diameter_pixels",
        "vertical_diameter_pixels",
        "radius_pixels",
        "radius_m",
        "horizontal_to_vertical_ratio",
        "strongly_non_circular",
    )
    with (analysis_directory / "bubble_radii.csv").open(
        "x", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=radius_fields)
        writer.writeheader()
        writer.writerows(radius_measurements)

    with (analysis_directory / "density_measurements.csv").open(
        "x", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            ("measurement_number", "density_kg_m3", "source")
        )
        writer.writerows(
            (
                index,
                value,
                "user-entered genuine experimental measurement",
            )
            for index, value in enumerate(density_measurements, start=1)
        )

    with (analysis_directory / "comparison.csv").open(
        "x", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=("quantity", "value", "uncertainty", "unit", "status"),
        )
        writer.writeheader()
        writer.writerows(table_rows)

    position_figure, position_axis = plt.subplots()
    position_axis.plot(
        [row["time_seconds"] for row in positions],
        [row["upward_displacement_m"] for row in positions],
        marker="o",
        linestyle="-",
    )
    position_axis.set_xlabel("Time (s)")
    position_axis.set_ylabel("Upward displacement (m)")
    position_axis.set_title(f"{run.fluid} bubble position vs. time")
    position_axis.grid(True)
    position_figure.tight_layout()
    position_figure.savefig(
        analysis_directory / "position_vs_time.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(position_figure)

    velocity_figure, velocity_axis = plt.subplots()
    if intervals:
        velocity_times = [row["midpoint_time_seconds"] for row in intervals]
        velocity_values = [row["velocity_m_s"] for row in intervals]
        velocity_axis.plot(
            velocity_times, velocity_values, marker="o", linestyle="-"
        )
        selected_times = [
            row["midpoint_time_seconds"]
            for row in intervals
            if row["selected_for_terminal_velocity"]
        ]
        if selected_times:
            selected_values = [
                row["velocity_m_s"]
                for row in intervals
                if row["selected_for_terminal_velocity"]
            ]
            velocity_axis.plot(
                selected_times,
                selected_values,
                marker="o",
                linestyle="none",
                color="red",
                label="Selected terminal-velocity range",
            )
            velocity_axis.legend()
    else:
        velocity_axis.text(
            0.5,
            0.5,
            "INCOMPLETE: at least two positions are needed",
            ha="center",
            va="center",
            transform=velocity_axis.transAxes,
        )
    velocity_axis.set_xlabel("Midpoint time (s)")
    velocity_axis.set_ylabel("Upward velocity (m/s)")
    velocity_axis.set_title(f"{run.fluid} bubble velocity vs. time")
    velocity_axis.grid(True)
    velocity_figure.tight_layout()
    velocity_figure.savefig(
        analysis_directory / "velocity_vs_time.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(velocity_figure)

    density_deviation = results["density_sample_standard_deviation_kg_m3"]
    density_note = (
        "Density standard deviation uses at least five genuine readings."
        if density_deviation is not None
        else "Density standard deviation is INCOMPLETE: fewer than five genuine readings."
    )
    propagated_uncertainty = results["viscosity_partial_uncertainty_pa_s"]
    if propagated_uncertainty is None:
        propagation_note = (
            "Viscosity uncertainty is INCOMPLETE because radius and/or selected "
            "velocity sample standard deviations are unavailable."
        )
    elif density_deviation is None:
        propagation_note = (
            "PARTIAL propagation includes radius and selected-velocity spread only; "
            "liquid-density uncertainty is unavailable and was not set to zero."
        )
    else:
        propagation_note = (
            "PARTIAL propagation includes radius, liquid-density, and selected-velocity "
            "sample standard deviations."
        )

    complete_equation = (
        "sigma_mu = mu * sqrt((2*sigma_R/R)^2 + "
        "(sigma_rho_liquid/(rho_liquid-rho_air))^2 + "
        "(sigma_rho_air/(rho_liquid-rho_air))^2 + "
        "(sigma_v/v)^2 + (sigma_g/g)^2)"
    )
    summary = [
        "Laboratory 1 - Viscosity analysis",
        "",
        f"Fluid: {run.fluid}",
        f"Original video: {run.video_info.path}",
        f"Calibration: {run.calibration_path}",
        f"Tracking measurements: {tracking_path}",
        f"Analysis folder: {analysis_directory}",
        "",
        "Comparison table (value +/- sample standard deviation when available):",
    ]
    for row in table_rows:
        summary.append(
            f"{row['quantity']}: {row['value']} +/- {row['uncertainty']} "
            f"{row['unit']} — {row['status']}"
        )
    summary.extend(
        [
            "",
            density_note,
            f"Density measurements entered: {len(density_measurements)} genuine value(s).",
            f"Bubble-radius measurements accepted: {len(radius_measurements)}.",
            (
                "Terminal-velocity intervals: "
                f"{terminal['start_interval_number']} through "
                f"{terminal['end_interval_number']} (user selected)."
                if terminal is not None
                else "Terminal-velocity interval selection: INCOMPLETE."
            ),
            "",
            "Approximate Stokes equation:",
            "mu = 2 * R^2 * (rho_liquid - rho_air) * g / (9 * v_terminal)",
            "SI units: R in m, density in kg/m^3, g in m/s^2, velocity in m/s, "
            "viscosity in Pa*s.",
            "Assumed air density: 1.2 kg/m^3. Assumed gravity: 9.81 m/s^2.",
            "",
            "Complete independent-input uncertainty equation:",
            complete_equation,
            propagation_note,
            "The uncertainty uses sample standard deviations of repeated "
            "measurements as spread estimates. Density uncertainty is included "
            "only when at least five genuine density readings were entered.",
            "The reported uncertainty is PARTIAL. It excludes calibration "
            "uncertainty, uncertainty in assumed air density and gravity, "
            "measurement bias, and possible systematic errors.",
            "Stokes' equation is approximate and assumes a spherical bubble, "
            "low-Reynolds-number flow, and negligible wall effects.",
        ]
    )
    with (analysis_directory / "summary.txt").open(
        "x", encoding="utf-8"
    ) as output_file:
        output_file.write("\n".join(summary) + "\n")

    return analysis_directory, table_rows


def main():
    fluid = choose_fluid()
    if fluid is None:
        print("Selection cancelled.")
        return 0

    mode = choose_experiment_mode()
    if mode is None:
        print("Experiment selection cancelled.")
        return 0

    try:
        if mode == "1":
            run = start_new_experiment(fluid)
        else:
            run = continue_existing_experiment(fluid)
    except tk.TclError as error:
        print(f"\nError opening an interactive window: {error}")
        return 1
    if run is None:
        return 0

    previous_files = existing_tracking_files(run)
    attempt_number, tracking_path = next_tracking_attempt(run, previous_files)
    if previous_files:
        print(
            "\nPrevious tracking measurements were found:"
        )
        for previous_path in previous_files:
            print(f"  {previous_path.name}")
        if not confirm_new_tracking_attempt(attempt_number, tracking_path):
            print("No new tracking attempt was started.")
            return 0

    print(f"\nCreating tracking attempt {attempt_number}.")
    print(f"New measurements will be saved to: {tracking_path}")

    try:
        measurements = track_bubble(run, tracking_path)
    except FileExistsError as error:
        print(f"\n{error}")
        return 0
    except (FileNotFoundError, RuntimeError, ValueError, cv2.error, tk.TclError) as error:
        print(f"\nError during bubble tracking: {error}")
        return 1

    if measurements is None:
        print("Bubble tracking cancelled. No tracking file was saved.")
        return 0
    if not measurements:
        print("No frames were accepted. No tracking file was saved.")
        return 0

    preview_tracking(measurements)
    if not confirm_tracking_save(len(measurements), tracking_path):
        print("Tracking measurements were not saved.")
        return 0

    try:
        tracking_path = save_tracking(measurements, tracking_path)
    except FileExistsError:
        print(
            f"\n{tracking_path.name} already exists in this run. "
            "The existing file was not overwritten."
        )
        return 0
    except OSError as error:
        print(f"\nError saving tracking measurements: {error}")
        return 1

    print(f"Tracking measurements saved to: {tracking_path}")
    try:
        positions, intervals = calculate_position_velocity(measurements)
        show_velocity_plot(intervals)
        terminal = choose_terminal_velocity(intervals)
        radius_measurements = collect_radius_measurements(run)
        density_measurements = collect_density_measurements()
        results = calculate_lab_results(
            radius_measurements, density_measurements, terminal
        )
        table_rows = result_table_rows(
            {**results, "radius_measurements": radius_measurements}
        )
        print_result_table(table_rows)
        analysis_directory, _ = save_analysis_results(
            run,
            tracking_path,
            positions,
            intervals,
            radius_measurements,
            density_measurements,
            terminal,
            results,
        )
    except (OSError, RuntimeError, ValueError, cv2.error, tk.TclError) as error:
        print(f"\nError completing the analysis: {error}")
        print(f"The accepted tracking data remains saved at: {tracking_path}")
        return 1

    print(f"\nAnalysis files saved in: {analysis_directory}")
    print("Graphs: position_vs_time.png and velocity_vs_time.png")
    print("Numerical data: position_vs_time.csv, velocity_vs_time.csv,")
    print("                bubble_radii.csv, density_measurements.csv, comparison.csv")
    print("Summary: summary.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
