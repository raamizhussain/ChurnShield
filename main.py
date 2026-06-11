import time
import sys
import subprocess

def run_step(script_name):
    print(f"\n======== EXECUTING: {script_name} ========")
    start_time = time.time()
    
    import os
    venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    try:
        result = subprocess.run(
            [python_exe, script_name],
            check=True,
            capture_output=False
        )
        elapsed = time.time() - start_time
        print(f"STATUS: Success | Duration: {elapsed:.2f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"CRITICAL ERROR in {script_name}: {e}")
        return False

def main():
    print("🚀 STARTING CHURNSHIELD PRODUCTION PIPELINE EXECUTION ENGINE 🚀")
    pipeline_start = time.time()
    
    from flush_tables import flush_all_tables
    try:
        flush_all_tables()
    except Exception as e:
        print(f"Aborting pipeline. Database flush failed: {e}")
        sys.exit(1)
        
    steps = [
        "ingest_raw_data.py",
        "create_indexes.py",  # Added optimization layer
        "populate_dim_customer.py",
        "populate_fact_activity.py",
        "calculate_velocity_features.py",
        "train_survival_model.py",
        "train_uplift_model.py"
    ]
    
    for step in steps:
        success = run_step(step)
        if not success:
            print(f"\n❌ PIPELINE EXECUTION HALTED AT STEP: {step} ❌")
            sys.exit(1)
            
    total_duration = time.time() - pipeline_start
    print(f"\n=======================================================")
    print(f"🎉 SUCCESS: Full Production Pipeline Completed Successfully! 🎉")
    print(f"Total Execution Runtime: {total_duration:.2f} seconds")
    print(f"=======================================================")

if __name__ == "__main__":
    main()