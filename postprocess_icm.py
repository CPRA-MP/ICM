import subprocess
import time


def postprocess_icm(
    script,
    *, #forces use of keywords for all command line args
    year,
    cpra_api,
    base_icm,
    model,
    grid_version,
    start_year,
    sterm,
    gterm
):
    print("=" * 50)
    print(f"Starting {script}")

    start = time.perf_counter()

    if script in [
        "postprocess_hydro.py",
        "postprocess_morph.py"
        ]:

        command = [
            str(cpra_api), #cpra api is needed for correct py env
            str(script),
            "--year", str(year),
            "--base_icm", str(base_icm),
            "--model", str(model),
            "--grid_version", str(grid_version),
            "--start_year", str(start_year),
            "--sterm", str(sterm),
            "--gterm", str(gterm)
        ]

    else:
        command = [
            str(cpra_api), #cpra api is needed for correct py env
            str(script),
            "--year", str(year),
            "--base_icm", str(base_icm),
            "--model", str(model),
            "--grid_version", str(grid_version),
            "--sterm", str(sterm),
            "--gterm", str(gterm)
        ]

    subprocess.call(command)

    elapsed = time.perf_counter() - start
    minutes = int(elapsed // 60)
    seconds = elapsed % 60
    print(f"Elapsed time for {script}: {minutes} minutes, {seconds:.2f} seconds")




