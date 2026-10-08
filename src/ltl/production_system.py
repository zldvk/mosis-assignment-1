import os
import pandas as pd
import mtl


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "..")
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "ltl", "production_system")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "ltl")


def load_trace(filepath):
    df = pd.read_csv(filepath)

    trace = {
        "m1_idle": list(zip(df["step"], df["m1_idle"].astype(bool))),
        "m1_busy": list(zip(df["step"], df["m1_busy"].astype(bool))),
        "m1_down": list(zip(df["step"], df["m1_down"].astype(bool))),
        "m1_repair": list(zip(df["step"], df["m1_repair"].astype(bool))),

        "m2_idle": list(zip(df["step"], df["m2_idle"].astype(bool))),
        "m2_busy": list(zip(df["step"], df["m2_busy"].astype(bool))),
        "m2_down": list(zip(df["step"], df["m2_down"].astype(bool))),
        "m2_repair": list(zip(df["step"], df["m2_repair"].astype(bool))),

        "tech_free": list(zip(df["step"], df["tech_free"].astype(bool))),
        "tech_busy": list(zip(df["step"], df["tech_busy"].astype(bool))),

        "p_in": list(zip(df["step"], df["p_in"].astype(bool))),
        "p_m1": list(zip(df["step"], df["p_m1"].astype(bool))),
        "p_m2": list(zip(df["step"], df["p_m2"].astype(bool))),
        "p_out": list(zip(df["step"], df["p_out"].astype(bool))),

        "idle": list(zip(df["step"], df["idle"].astype(bool))),
    }

    return trace


def evaluate_trace(trace):
    results = {}

    properties = {
        "m1_one_mode": mtl.parse(
            "G[0, 201] (((((m1_idle & ~m1_busy) & ~m1_down) & ~m1_repair) | ((((~m1_idle & m1_busy) & ~m1_down) & ~m1_repair) | (((((~m1_idle & ~m1_busy) & m1_down) & ~m1_repair) | (((~m1_idle & ~m1_busy) & ~m1_down) & m1_repair))))))"
        ),

        "m2_one_mode": mtl.parse(
            "G[0, 201] (((((m2_idle & ~m2_busy) & ~m2_down) & ~m2_repair) | ((((~m2_idle & m2_busy) & ~m2_down) & ~m2_repair) | (((((~m2_idle & ~m2_busy) & m2_down) & ~m2_repair) | (((~m2_idle & ~m2_busy) & ~m2_down) & m2_repair))))))"
        ),

        "max_one_part": mtl.parse(
            "G[0, 201] (((((idle & ~p_in) & ~p_m1) & ~p_m2) & ~p_out) | (((((~idle & p_in) & ~p_m1) & ~p_m2) & ~p_out) | (((((~idle & ~p_in) & p_m1) & ~p_m2) & ~p_out) | (((((~idle & ~p_in) & ~p_m1) & p_m2) & ~p_out) | ((((~idle & ~p_in) & ~p_m1) & ~p_m2) & p_out)))))"
        ),

        "not_both_in_repair": mtl.parse(
            "G[0, 201] ~(m1_repair & m2_repair)"
        ),

        "part_at_m1_mode": mtl.parse(
            "G[0, 201] (p_m1 -> (m1_busy | (m1_down | m1_repair)))"
        ),

        "machines_not_both_holding": mtl.parse(
            "G[0, 201] ~(p_m1 & p_m2)"
        ),

        "m1_before_m2": mtl.parse(
            "(~p_m2 W p_m1)"
        ),

        "eventually_shipped": mtl.parse(
            "F[0, 201] p_out"
        ),

        "wait_may_continue": mtl.parse(
            "G[0, 200] ((p_out & X idle) -> X (idle W p_in))"
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
        filename = f"production_system_{number}.csv"
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
        "production_system_ltl.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )




if __name__ == "__main__":
    main()