import os
import pandas as pd


TEAM_NAME_MAP = {
	# Add or edit mappings as needed
	"Delhi Daredevils": "Delhi Capitals",
	"Kings XI Punjab": "Punjab Kings",
	"Deccan Chargers": "Sunrisers Hyderabad",
}

PLAYER_NAME_MAP = {
	# Example: map legacy/alternate names to canonical names
	# "BB McCullum": "Brendon McCullum",
}


def _standardize_series(s: pd.Series, mapping: dict) -> pd.Series:
	if mapping:
		return s.replace(mapping)
	return s


def preprocess_data(deliveries_path: str, matches_path: str, out_dir: str = None):
	"""Load, clean and save deliveries and matches data.

	Cleaning performed:
	- Standardise team and player names via mapping dicts (edit mappings above).
	- Handle missing values for `winner`, `player_of_match`, and `result_margin`.
	- Remove `umpire1` and `umpire2` if present.
	- Save cleaned CSVs next to originals unless `out_dir` is provided.

	Returns: (deliveries_df, matches_df)
	"""
	deliveries = pd.read_csv(deliveries_path)
	matches = pd.read_csv(matches_path)

	# Standardise team names in both datasets
	team_cols_deliveries = [c for c in ["batting_team", "bowling_team"] if c in deliveries.columns]
	for c in team_cols_deliveries:
		deliveries[c] = _standardize_series(deliveries[c], TEAM_NAME_MAP)

	team_cols_matches = [c for c in ["team1", "team2", "toss_winner", "winner"] if c in matches.columns]
	for c in team_cols_matches:
		matches[c] = _standardize_series(matches[c], TEAM_NAME_MAP)

	# Standardise player names where relevant
	player_cols_deliveries = [c for c in ["batter", "bowler", "non_striker", "player_dismissed"] if c in deliveries.columns]
	for c in player_cols_deliveries:
		deliveries[c] = _standardize_series(deliveries[c], PLAYER_NAME_MAP)

	if "player_of_match" in matches.columns:
		matches["player_of_match"] = _standardize_series(matches["player_of_match"], PLAYER_NAME_MAP)

	# Handle missing values in matches: remove rows with missing winner, player_of_match, or result_margin
	# Identify match IDs to remove
	matches_to_remove = set()
	
	if "winner" in matches.columns:
		matches_to_remove.update(matches[matches["winner"].isna()]["id"].values)
	if "player_of_match" in matches.columns:
		matches_to_remove.update(matches[matches["player_of_match"].isna()]["id"].values)
	if "result_margin" in matches.columns:
		matches_to_remove.update(matches[matches["result_margin"].isna()]["id"].values)
	
	# Remove matches with missing values
	matches = matches[~matches["id"].isin(matches_to_remove)].reset_index(drop=True)
	
	# Remove corresponding rows from deliveries
	if "match_id" in deliveries.columns:
		deliveries = deliveries[~deliveries["match_id"].isin(matches_to_remove)].reset_index(drop=True)

	# Remove unnecessary columns if present
	for col in ["umpire1", "umpire2"]:
		if col in matches.columns:
			matches = matches.drop(columns=[col])

	# Prepare output paths
	base_deliveries = os.path.splitext(os.path.basename(deliveries_path))[0]
	base_matches = os.path.splitext(os.path.basename(matches_path))[0]
	out_dir = out_dir or os.path.dirname(deliveries_path)

	deliveries_out = os.path.join(out_dir, f"{base_deliveries}_cleaned.csv")
	matches_out = os.path.join(out_dir, f"{base_matches}_cleaned.csv")

	deliveries.to_csv(deliveries_out, index=False)
	matches.to_csv(matches_out, index=False)

	return deliveries, matches


if __name__ == "__main__":
	# Default runner: assumes files are in the same folder as this script
	folder = os.path.dirname(__file__)
	deliveries_path = os.path.join(folder, "deliveries.csv")
	matches_path = os.path.join(folder, "matches.csv")
	d, m = preprocess_data(deliveries_path, matches_path)
	print("Saved cleaned files.")


