import pandas as pd
import numpy as np

# Load the cleaned data
matches = pd.read_csv('matches_cleaned.csv')
deliveries = pd.read_csv('deliveries_cleaned.csv')

print("Generating detailed CSV reports...")

# ==================== TOP BATSMEN REPORT ====================
batsmen_stats = deliveries.groupby('batter').agg({
    'batsman_runs': 'sum',
    'ball': 'count',
}).rename(columns={'batsman_runs': 'runs', 'ball': 'balls_faced'})

fours = deliveries[deliveries['batsman_runs'] == 4].groupby('batter').size()
sixes = deliveries[deliveries['batsman_runs'] == 6].groupby('batter').size()

batsmen_stats['fours'] = fours
batsmen_stats['sixes'] = sixes
batsmen_stats = batsmen_stats.fillna(0).astype({'fours': int, 'sixes': int})
batsmen_stats['strike_rate'] = (batsmen_stats['runs'] / batsmen_stats['balls_faced'] * 100).round(2)
batsmen_stats = batsmen_stats.sort_values('runs', ascending=False)

batsmen_stats.to_csv('batsmen_detailed_stats.csv')
print("✓ Saved: batsmen_detailed_stats.csv")

# ==================== TOP BOWLERS REPORT ====================
bowlers_stats = pd.DataFrame()

wickets = deliveries[deliveries['is_wicket'] == 1].groupby('bowler').size()
balls_bowled = deliveries.groupby('bowler').size()
runs_conceded = deliveries.groupby('bowler')['total_runs'].sum()
dot_balls = deliveries[deliveries['bowler'].notna() & (deliveries['total_runs'] == 0)].groupby('bowler').size()

bowlers_stats['wickets'] = wickets
bowlers_stats['balls_bowled'] = balls_bowled
bowlers_stats['runs_conceded'] = runs_conceded
bowlers_stats['overs'] = (bowlers_stats['balls_bowled'] / 6).round(2)
bowlers_stats['economy_rate'] = (bowlers_stats['runs_conceded'] / (bowlers_stats['balls_bowled'] / 6)).round(2)
bowlers_stats['dot_balls'] = dot_balls
bowlers_stats['dot_ball_percentage'] = ((bowlers_stats['dot_balls'] / bowlers_stats['balls_bowled']) * 100).round(2)
bowlers_stats = bowlers_stats.fillna(0).astype({'wickets': int, 'dot_balls': int})
bowlers_stats = bowlers_stats.sort_values('wickets', ascending=False)

bowlers_stats.to_csv('bowlers_detailed_stats.csv')
print("✓ Saved: bowlers_detailed_stats.csv")

# ==================== TEAM RIVALRIES REPORT ====================
h2h_records = {}

for idx, row in matches.iterrows():
    team1 = row['team1']
    team2 = row['team2']
    winner = row['winner']
    
    teams = tuple(sorted([team1, team2]))
    
    if teams not in h2h_records:
        h2h_records[teams] = {'total': 0, team1: 0, team2: 0}
    
    h2h_records[teams]['total'] += 1
    
    if pd.notna(winner):
        if winner == team1 or winner == team2:
            h2h_records[teams][winner] += 1

h2h_list = []
for teams, record in h2h_records.items():
    h2h_list.append({
        'Team1': teams[0],
        'Team2': teams[1],
        f'{teams[0]}_Wins': record[teams[0]],
        f'{teams[1]}_Wins': record[teams[1]],
        'Total_Matches': record['total']
    })

h2h_df = pd.DataFrame(h2h_list).sort_values('Total_Matches', ascending=False)
h2h_df.to_csv('team_rivalries_h2h.csv', index=False)
print("✓ Saved: team_rivalries_h2h.csv")

# Team wins report
team_wins = matches[matches['winner'].notna()].groupby('winner').size().sort_values(ascending=False)
team_wins_df = pd.DataFrame({
    'Team': team_wins.index,
    'Total_Wins': team_wins.values
})
team_wins_df.to_csv('team_wins_overall.csv', index=False)
print("✓ Saved: team_wins_overall.csv")

# ==================== WINNING FACTORS REPORT ====================
toss_analysis = matches[matches['winner'].notna()].copy()
toss_analysis['toss_won'] = toss_analysis['toss_winner'] == toss_analysis['winner']
toss_analysis['toss_decision'] = toss_analysis['toss_decision']

toss_decision_impact = toss_analysis.groupby('toss_decision').agg({
    'toss_won': ['sum', 'count']
}).to_dict()

toss_decision_stats = []
for decision in toss_analysis['toss_decision'].unique():
    if pd.notna(decision):
        subset = toss_analysis[toss_analysis['toss_decision'] == decision]
        wins = subset['toss_won'].sum()
        total = len(subset)
        win_pct = (wins / total * 100) if total > 0 else 0
        
        toss_decision_stats.append({
            'Decision': decision,
            'Wins_When_Toss_Won': wins,
            'Total_Matches': total,
            'Win_Percentage': round(win_pct, 2)
        })

toss_decision_df = pd.DataFrame(toss_decision_stats)
toss_decision_df.to_csv('toss_decision_impact.csv', index=False)
print("✓ Saved: toss_decision_impact.csv")

# Venue analysis
venue_stats = matches[matches['winner'].notna()].groupby('venue').agg({
    'id': 'count',
    'winner': 'count'
}).rename(columns={'id': 'total_matches', 'winner': 'decided_matches'})
venue_stats = venue_stats.sort_values('total_matches', ascending=False)
venue_stats.to_csv('venue_statistics.csv')
print("✓ Saved: venue_statistics.csv")

# Season analysis
season_stats = matches.groupby('season').agg({
    'id': 'count',
    'winner': lambda x: x.notna().sum()
}).rename(columns={'id': 'total_matches', 'winner': 'decided_matches'})
season_stats = season_stats.sort_index()
season_stats.to_csv('season_statistics.csv')
print("✓ Saved: season_statistics.csv")

print("\n" + "="*50)
print("All detailed reports generated successfully!")
print("="*50)
