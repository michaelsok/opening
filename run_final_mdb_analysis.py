
from src.opening.user_opening_analysis import analyze_user_openings
from datetime import datetime, timedelta

def run_analysis():
    # Last week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"Analyzing games for ChessMDB from {start_date.date()} to {end_date.date()}...")
    
    try:
        report_path = analyze_user_openings(
            username="ChessMDB",
            opening_repertoire="openings",
            time_class="blitz",
            start_date=start_date,
            end_date=end_date,
            output_file="reports/chessmdb_refined_analysis.html",
            open_in_browser=False
        )
        print(f"Success! Refined report generated at: {report_path}")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    run_analysis()
