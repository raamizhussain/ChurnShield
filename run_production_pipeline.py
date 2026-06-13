import sys
import subprocess
import time

def execute_pipeline_step(script_name):
    print(f"\n==================================================================")
    print(f"STAGE START: Executing {script_name}...")
    print(f"==================================================================")
    
    start_time = time.time()
    
    try:
        process = subprocess.run(
            [sys.executable, script_name],
            check=True,
            text=True,
            capture_output=False
        )
        duration = time.time() - start_time
        print(f"STAGE SUCCESS: {script_name} completed in {duration:.2f} seconds.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"STAGE CRITICAL FAILURE: {script_name} aborted with exit code {e.returncode}")
        return False

def main():
    pipeline_start = time.time()
    print("==================================================================")
    print("      CHURNSHIELD ENTERPRISE END-TO-END ORCHESTRATION LOOP        ")
    print("==================================================================")
    
    pipeline_steps = [
        "scrape_competitor_sentiment.py",
        "ingest_production_scd2.py",
        "calculate_velocity_features.py",
        "alert_dispatch_system.py"
    ]
    
    for step in pipeline_steps:
        success = execute_pipeline_step(step)
        if not success:
            print("\nPIPELINE EXECUTION ABORTED: Hard dependency breakdown encountered.")
            sys.exit(1)
            
    total_duration = time.time() - pipeline_start
    print(f"\n==================================================================")
    print(f"PIPELINE RUN COMPLETE: All layers synchronized in {total_duration:.2f}s.")
    print("==================================================================")

if __name__ == "__main__":
    main()