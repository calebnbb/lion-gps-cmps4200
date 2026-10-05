# Lion GPS - AI Technical Spike (Phase 2)

Tests Claude Sonnet + all-MiniLM-L6-v2 on 6 realistic advising questions and 7 failure conditions, plus parsing a sample audit PDF.

## Run it (about 2 minutes, costs a few cents)
```bash
cd spike
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."      # from console.anthropic.com
python lion_gps_spike.py --runs 3          # 3 runs = 18 calls, steadier averages
```
First run downloads all-MiniLM-L6-v2 (~90 MB).

## Outputs (`results/`)
- `spike_summary.md` - the one-page summary, numbers filled in. Finish the two "fill in" lines (manual quality review, keep/switch decision).
- `spike_log.md` - every question, retrieved records, raw answer, and every error message.
- `spike_results.json` - raw data.

`--mock` runs the pipeline offline with a fake model. Use it only to check your setup; its numbers are not valid spike data.

## Files
- `sample_data.py` - mock degree audit (Chidi persona), catalog requirements, Spring 2027 schedule, test questions
- `sample_audit.pdf` - mock Workday-style progress report (Ngozi persona) for the upload test. If it is missing, run `python make_sample_audit.py` to create it.
- `lion_gps_spike.py` - the spike
