import os
import pandas as pd
import mtl


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "..")
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "ltl", "simple_traffic_light")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "ltl")


def load_trace(filepath):
    df = pd.read_csv(filepath)

    trace = {
        "red": list(zip(df["step"], df["red"].astype(bool))),
        "yellow": list(zip(df["step"], df["yellow"].astype(bool))),
        "green": list(zip(df["step"], df["green"].astype(bool))),
        "alternate": list(zip(df["step"], df["alternate"].astype(bool))),
    }

    return trace


def evaluate_trace(trace):
    results = {}

    properties = {
        "one_lamp": mtl.parse(
            "G[0, 201] ((((red & ~yellow) & ~green) | (((~red & yellow) & ~green) | ((~red & ~yellow) & green))))"
        ),

        "starts_red": mtl.parse(
            "red"
        ),

        "always_red": mtl.parse(
            "G[0, 201] red"
        ),

        "eventually_green": mtl.parse(
            "F[0, 201] green"
        ),

        "red_stays_or_next_yellow": mtl.parse(
            "G[0, 200] (red -> X (red | yellow))"
        ),

        "no_red_to_green": mtl.parse(
            "G[0, 200] (red -> X ~green)"
        ),

        "no_green_to_red": mtl.parse(
            "G[0, 200] (green -> X ~red)"
        ),

        "yellow_opens_to_green": mtl.parse(
            "G[0, 200] (((yellow & ~alternate) & X ~yellow) -> X green)"
        ),

        "yellow_returns_to_red": mtl.parse(
            "G[0, 200] (((yellow & alternate) & X ~yellow) -> X red)"
        ),

        "yellow_after_red_may_wait": mtl.parse(
            "G[0, 200] ((red & X yellow) -> X (yellow W green))"
        ),
    }

    for property_name, formula in properties.items():
        result = formula(
            trace,
            time=0,
            quantitative=False,
            dt=1
        )


        results[property_name] = str(bool(result)).lower()

    return results



def main():
    all_results = []

    for number in range(1, 11):
        filename = f"simple_traffic_light_{number}.csv"
        filepath = os.path.join(DATA_DIR, filename)

        print(f"Checking {filename}...")

        trace = load_trace(filepath)
        results = evaluate_trace(trace)

        row = {
            "trace": filename,
            **results
        }

        all_results.append(row)


    results_df = pd.DataFrame(all_results)

    output_file = os.path.join(
        RESULTS_DIR,
        "simple_traffic_light_ltl.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )




if __name__ == "__main__":
    main()